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
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from peer.entity.feeds import EntitiesFeed
from peer.entity.forms import EntityGroupForm
from peer.entity.models import Entity, EntityGroup
from peer.entity.paginator import paginated_list_of_entities
from peer.entity.security import can_edit_entity_group


@login_required
def entity_group_add(request, return_view_name='entities:entity_group_view'):
    if request.method == 'POST':
        form = EntityGroupForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            messages.success(request, _(u'Entity group created'))
            return HttpResponseRedirect(
                reverse(return_view_name, args=[instance.id])
            )
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))

    else:
        form = EntityGroupForm()

    return render_to_response('entity/edit_entity_group.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def entity_group_view(request, entity_group_id):
    entity_group = get_object_or_404(EntityGroup, id=entity_group_id)
    queries = entity_group.query.split('&')
    entities_in_group = Entity.objects.xpath_filters(queries)

    # Can't do it at the model because of circular dependency
    entity_group.feed_url = EntitiesFeed().link() + '?xpath=' + entity_group.query

    entities = paginated_list_of_entities(request, entities_in_group)

    return render_to_response('entity/view_entity_group.html', {
        'entity_group': entity_group,
        'entities': entities,
    }, context_instance=RequestContext(request))


@login_required
def entity_group_edit(request, entity_group_id,
        return_view_name='entities:entity_group_view'):

    entity_group = get_object_or_404(EntityGroup, id=entity_group_id)

    if not can_edit_entity_group(request.user, entity_group):
        raise PermissionDenied

    if request.method == 'POST':
        form = EntityGroupForm(request.POST, instance=entity_group)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'Entity group edited succesfully'))
            return HttpResponseRedirect(
                reverse(return_view_name, args=[form.instance.id])
            )
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))

    else:
        form = EntityGroupForm(instance=entity_group)

    return render_to_response('entity/edit_entity_group.html', {
        'entity_group': entity_group,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def entity_group_remove(request, entity_group_id,
                        return_view_name='account_profile'):

    entity_group = get_object_or_404(EntityGroup, id=entity_group_id)

    if not can_edit_entity_group(request.user, entity_group):
        raise PermissionDenied

    if request.method == 'POST':
        entity_group.delete()
        messages.success(request, _('Entity group removed succesfully'))
        return HttpResponseRedirect(reverse(return_view_name))

    return render_to_response('entity/remove_entity_group.html', {
        'entity_group': entity_group,
    }, context_instance=RequestContext(request))
