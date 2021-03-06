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

import uuid
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from peer.domain.forms import DomainForm
from peer.domain.models import Domain, DomainTeamMembership, DomainToken
from peer.domain.models import DomainTeamMembershipRequest
from peer.entity.models import Entity
from peer.domain.utils import (send_mail_for_validation,
                               send_notification_mail_to_domain_owner,
                               get_administrative_emails_from_settings,
                               get_administrative_emails_from_whois,
                               send_mail)
from peer.domain.validation import (http_validate_ownership,
                                    dns_validate_ownership,
                                    email_validate_ownership,
                                    check_domain_token,
                                    check_superdomain_verified)


@login_required
def domain_add(request):
    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            messages.success(request, _(u'Domain created'))
            instance = form.save(commit=False)
            instance.owner = request.user
            if check_superdomain_verified(instance):
                return _domain_validate(request, instance)
            instance.save()
            return HttpResponseRedirect(
                reverse('domain_verify',
                        kwargs={'domain_id': instance.id}))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))

    else:
        form = DomainForm()

    return render_to_response('domain/add.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def domain_verify(request, domain_id, token=False):
    domain = get_object_or_404(Domain, id=domain_id, owner=request.user)
    valid = False
    check = False
    if request.method == 'POST':
        check = True
        if u'http' in request.POST:
            valid = (http_validate_ownership(domain.validation_url, domain.validation_key) or
                     http_validate_ownership(domain.validation_url_with_www_prefix, domain.validation_key))
            if not valid:
                messages.error(
                    request, _(u'Error HTTP validation: Unreachable URL or the validation-code was not found'))
        elif u'https' in request.POST:
            valid = (http_validate_ownership(domain.validation_secure_url, domain.validation_key) or
                     http_validate_ownership(domain.validation_secure_url_with_www_prefix, domain.validation_key))
            if not valid:
                messages.error(
                    request, _(u'Error HTTPs validation: Unreachable URL or the validation-code was not found'))
        elif u'dns' in request.POST:
            valid = dns_validate_ownership(domain.name, domain.validation_key, request=request)
            if not valid:
                messages.info(
                    request, _(u'Do not try again until the zone has been propagated and the DNS cached cleaned'))
        elif u'email' in request.POST:
            check = False
            token = uuid.uuid4().hex
            DomainToken.objects.create(domain=domain.name, token=token)
            send_mail_for_validation(request, domain, token, request.POST.get('mail'))
            messages.success(
                request, _(u'An email has been sent to %(domain_email)s') % {'domain_email': request.POST.get('mail')})
        else:
            raise ValueError("No validation mode selected'.")

    if request.method == 'GET' and token:
        check = True
        valid = email_validate_ownership(domain.name, token)
        if not valid:
            messages.warning(
                request, _(u'Error Email validation: Invalid token provided'))

    if check:
        if valid:
            return _domain_validate(request, domain)
        else:
            messages.error(
                request, _(u'Error while checking domain ownership'))

    domain_contact_list = get_administrative_emails_from_whois(domain.name)

    whois_has_emails = False
    if domain_contact_list:
        whois_has_emails = True

    domain_contact_list += get_administrative_emails_from_settings(domain.name)
    domain_contact_list = list(set(domain_contact_list))

    return render_to_response('domain/verify.html', {
        'domain': domain,
        'domain_contact_list': domain_contact_list,
        'whois_has_emails': whois_has_emails,
    }, context_instance=RequestContext(request))


def _domain_validate(request, domain):
    domain.validated = True
    domain.save()
    if getattr(settings, 'NOTIFY_DOMAIN_OWNER', False):
        token = uuid.uuid4().hex
        DomainToken.objects.create(domain=domain.name, token=token)
        send_notification_mail_to_domain_owner(request, domain, token)
    messages.success(
        request, _(u'The domain ownership was successfully verified'))
    return HttpResponseRedirect(reverse('account_profile'))


def domain_invalidate(request, domain_id, token):
    domain = get_object_or_404(Domain, id=domain_id)
    if check_domain_token(domain.name, token):
        domain.validated = False
        domain.save()
        messages.success(
            request, _(u'The domain was successfully invalidated'))
    else:
        messages.error(
            request, _(u'Error while checking token, the domain is still active'))
    return HttpResponseRedirect(reverse('index'))


@login_required
def domain_remove(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    if domain.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        domain.delete()
        messages.success(request, _('Domain removed succesfully'))
        return HttpResponseRedirect(reverse('account_profile'))

    return render_to_response('domain/remove.html', {
        'domain': domain,
        'entities': domain.entity_set.all(),
    }, context_instance=RequestContext(request))


@login_required
def force_domain_ownership(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    if not request.user.is_superuser or domain.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        domain.validated = True
        domain.save()
        messages.success(request, _('Domain ownership set by force as verified'))
        return HttpResponseRedirect(reverse('manage_domain', args=[domain.id]))

    return render_to_response('domain/force_ownership.html', {
        'domain': domain,
    }, context_instance=RequestContext(request))


@login_required
def manage_domain(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    if domain.owner != request.user:
        raise PermissionDenied

    if request.user.is_superuser and domain.validated:
        return manage_domain_team(request, domain_id)

    return domain_verify(request, domain_id)


# DOMAIN SHARING

def can_share_domain(user, domain):
    return user.is_superuser and domain.validated and user == domain.owner


@login_required
def manage_domain_team(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    if not can_share_domain(request.user, domain):
        raise PermissionDenied

    return render_to_response('domain/sharing.html', {
        'domain': domain,
    }, context_instance=RequestContext(request))


@login_required
def request_membership(request, domain_id, username):
    domain = Domain.objects.get(pk=domain_id)
    user = User.objects.get(username=username)
    member_request = DomainTeamMembershipRequest(domain=domain, requester=user)
    member_request.save()
    url = request.build_absolute_uri(reverse('list_membership_requests'))
    subject = _('Domain team membership request')
    data = {'username': user.username, 'domain_name': domain.name, 'url': url}
    admins = User.objects.filter(is_superuser=True, domains=domain)
    admin_emails = [admin.email for admin in admins]
    send_mail(subject, data, 'membership_request', admin_emails)
    return HttpResponseRedirect(reverse('account_profile'))


@login_required
def list_membership_requests(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    # first remove stale entries
    timeout = settings.MEMBERSHIP_REQUEST_TTL
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=timeout)
    expired = now - delta
    DomainTeamMembershipRequest.objects.filter(date__lte=expired).delete()

    # then show remaining
    membership_requests = DomainTeamMembershipRequest.objects.filter(domain__owner=request.user)
    return render_to_response('domain/list_membership_requests.html', {
        'membership_requests': membership_requests,
    }, context_instance=RequestContext(request))


@login_required
def accept_membership_request(request, domain_id, username):
    if not request.user.is_superuser:
        raise PermissionDenied

    _add_delegate(request, domain_id, username)
    domain = Domain.objects.get(pk=domain_id)
    requester = User.objects.get(username=username)
    DomainTeamMembershipRequest.objects.filter(domain=domain,
                                             requester=requester).delete()

    email = requester.email
    subject = _('Domain team membership request ACCEPTED')
    data = {'domain_name': domain.name}
    send_mail(subject, data, 'membership_request_accepted', [email])

    return HttpResponseRedirect(reverse('list_membership_requests'))


@login_required
def reject_membership_request(request, domain_id, username):
    if not request.user.is_superuser:
        raise PermissionDenied

    domain = Domain.objects.get(pk=domain_id)
    requester = User.objects.get(username=username)
    DomainTeamMembershipRequest.objects.filter(domain=domain,
                                             requester=requester).delete()

    email = requester.email
    subject = _('Domain team membership request REJECTED')
    data = {'domain_name': domain.name}
    send_mail(subject, data, 'membership_request_rejected', [email])

    return HttpResponseRedirect(reverse('list_membership_requests'))


@login_required
def list_delegates(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    if not can_share_domain(request.user, domain):
        raise PermissionDenied

    return render_to_response('domain/list_delegates.html', {
        'domain': domain,
        'delegates': domain.team.all(),
    }, context_instance=RequestContext(request))


def _add_delegate(request, domain_id, username):
    domain = get_object_or_404(Domain, id=domain_id)
    if not can_share_domain(request.user, domain):
        raise PermissionDenied

    user = User.objects.get(username=username)
    if user:
        if user in domain.team.all():
            return HttpResponse('delegate')
        else:
            membership = DomainTeamMembership(domain=domain, member=user)
            membership.save()

@login_required
def add_delegate(request, domain_id, username):
    _add_delegate(request, domain_id, username)
    return list_delegates(request, domain_id)


@login_required
def remove_delegate(request, domain_id, username):
    domain = get_object_or_404(Domain, id=domain_id)
    if not can_share_domain(request.user, domain):
        raise PermissionDenied

    user = User.objects.get(username=username)
    if user:
        if user not in domain.team.all():
            return HttpResponse('notdelegate')
        else:
            entities = Entity.objects.filter(owner=user)
            for entity in entities:
                if entity.domain == domain:
                    return HttpResponse('hasentities')

            membership = DomainTeamMembership.objects.get(domain=domain,
                                                          member=user)
            membership.delete()

    return list_delegates(request, domain_id)
