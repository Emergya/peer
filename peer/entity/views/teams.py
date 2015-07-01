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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from peer.entity.models import Entity, PermissionDelegation
from peer.entity.security import can_change_entity_team


@login_required
def sharing(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    return render_to_response('entity/sharing.html', {
        'entity': entity,
    }, context_instance=RequestContext(request))


@login_required
def list_delegates(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    return render_to_response('entity/delegate_list.html', {
        'delegates': entity.delegates.all(),
        'entity_id': entity.pk,
    }, context_instance=RequestContext(request))


@login_required
def remove_delegate(request, entity_id, user_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    delegate = User.objects.get(pk=user_id)
    if entity and delegate:
        delegations = PermissionDelegation.objects.filter(entity=entity,
                                                          delegate=delegate)
        for delegation in delegations:
            delegation.delete()
    return list_delegates(request, entity_id)


@login_required
def add_delegate(request, entity_id, username):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    new_delegate = User.objects.get(username=username)
    if entity and new_delegate:
        pd = PermissionDelegation.objects.filter(entity=entity,
                                                 delegate=new_delegate)
        if not pd and new_delegate != entity.owner:
            pd = PermissionDelegation(entity=entity, delegate=new_delegate)
            pd.save()
        elif pd:
            return HttpResponse('delegate')
        else:
            return HttpResponse('owner')
    return list_delegates(request, entity_id)


@login_required
def make_owner(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_change_entity_team(request.user, entity):
        raise PermissionDenied

    old_owner = entity.owner
    new_owner_id = request.POST.get('new_owner_id')
    if new_owner_id:
        new_owner = User.objects.get(pk=int(new_owner_id))
        if new_owner:
            entity.owner = new_owner
            entity.save()
            msg = _('New owner successfully set')
            old_pd = PermissionDelegation.objects.get(entity=entity,
                                                      delegate=new_owner)
            if old_pd:
                old_pd.delete()
            if old_owner:
                new_pd = PermissionDelegation.objects.filter(entity=entity,
                                                             delegate=old_owner)
                if not new_pd:
                    new_pd = PermissionDelegation(entity=entity,
                                                  delegate=old_owner)
                    new_pd.save()
        else:
            msg = _('User not found')
    else:
        msg = _('You must provide the user id of the new owner')
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('entities:entity_view',
                                         args=(entity_id,)))
