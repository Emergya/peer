# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Terena.

import json

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import logout as auth_logout
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.translation import ugettext as _

from djangosaml2.views import logout as saml2_logout

from registration.backends.default.views import RegistrationView

from peer.account.forms import PersonalInformationForm
from peer.account.forms import FriendInvitationForm
from peer.account.forms import RegistrationFormCaptchaTOU
from peer.account.templatetags.account import safefullname
from peer.domain.models import Domain
from peer.entity.models import Entity
from peer.entity.models import PermissionDelegation
from peer.entity.models import EntityGroup


@login_required
def profile(request):
    domains = Domain.objects.filter(owner=request.user)
    owned_entities = Entity.objects.filter(owner=request.user)
    owned_group_entities = EntityGroup.objects.filter(owner=request.user)
    delegations = PermissionDelegation.objects.filter(delegate=request.user)
    return render_to_response('account/profile.html', {
        'domains': domains,
        'owned_entities': owned_entities,
        'permission_delegations': delegations,
        'owned_group_entities': owned_group_entities,
    }, context_instance=RequestContext(request))


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = PersonalInformationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Changes saved succesfully'))
            return HttpResponseRedirect(reverse('account_profile'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        form = PersonalInformationForm(instance=request.user)

    return render_to_response('account/edit.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def invite_friend(request):
    sendername = request.user.get_full_name() or request.user.username
    if request.method == 'POST':
        form = FriendInvitationForm(request.POST)
        if form.is_valid():
            email = form['destinatary'].data
            body = form['body_text'].data.encode('utf8')
            subject = _(u'%s invites you to the Peer project') % sendername
            send_mail(subject, body,  settings.DEFAULT_FROM_EMAIL, [email])
            messages.success(request,
                             _('Invitation message sent to %s') % email)
            return HttpResponseRedirect(reverse('account_profile'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        body = render_to_string('account/invitation_email.txt',
                                {
                                    'site': get_current_site(request),
                                    'user': sendername,
                                })
        form = FriendInvitationForm(initial={'body_text': body})

    return render_to_response('account/invite_friend.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def _user_search(q):
    if q:
        query = None
        terms = q.split()
        for term in terms:
            queries = Q(username__icontains=term) | \
                Q(first_name__icontains=term) | \
                Q(last_name__icontains=term)
            query = query and (query & queries) or queries

        return User.objects.filter(query)
    return []


def search_users_auto(request):
    q = request.GET.get('term', '')
    users = _user_search(q)
    names = [{'value': u.username, 'label': safefullname(u)} for u in users]
    return HttpResponse(json.dumps(names))


def logout(request):
    if (getattr(settings, 'SAML_ENABLED', False) and
            BACKEND_SESSION_KEY in request.session and
            request.session[BACKEND_SESSION_KEY] == 'djangosaml2.backends.Saml2Backend'):
        return saml2_logout(request)
    else:
        return auth_logout(request, template_name='registration/logout.html')


@login_required
def manage_admin_team(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    return render_to_response('account/manage_admin_team.html', {},
                              context_instance=RequestContext(request))


@login_required
def list_superusers(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    return render_to_response('account/list_superusers.html', {
        'superusers': User.objects.filter(is_superuser=True),
    }, context_instance=RequestContext(request))


@login_required
def add_superuser(request, username):
    if not request.user.is_superuser:
        raise PermissionDenied

    new_superuser = User.objects.get(username=username)
    if new_superuser:
        if new_superuser.is_superuser:
            return HttpResponse('superuser')
        else:
            new_superuser.is_superuser = True
            new_superuser.save()
    return list_superusers(request)


@login_required
def remove_superuser(request, username):
    if not request.user.is_superuser:
        raise PermissionDenied

    new_superuser = User.objects.get(username=username)
    if new_superuser:
        if new_superuser.username == 'admin':
            return HttpResponse('adminuser')
        elif new_superuser.is_superuser:
            for domain in Domain.objects.filter(owner=new_superuser):
                if domain.team.count():
                    return HttpResponse('delegateddomains')
            new_superuser.is_superuser = False
            new_superuser.save()
        else:
            return HttpResponse('notsuperuser')
    return list_superusers(request)


class RegistrationCaptchaView(RegistrationView):
    form_class = RegistrationFormCaptchaTOU
