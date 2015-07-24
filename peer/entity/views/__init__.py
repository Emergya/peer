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

from peer.account.templatetags.account import authorname
from peer.domain.models import Domain
from peer.entity.forms import EntityForm
from peer.entity.models import Entity, EntityMD, AttributesMD
from peer.entity.paginator import paginated_list_of_entities
from peer.entity.security import can_edit_entity
from peer.entity.utils import add_previous_revisions


def entities_list(request):
    entities = Entity.objects.all()
    paginated_entities = paginated_list_of_entities(request, entities)

    return render_to_response('entity/list.html', {
        'entities': paginated_entities,
    }, context_instance=RequestContext(request))


@login_required
def entity_add(request):
    return entity_add_with_domain(request, None, 'entities:edit_metadata')


@login_required
def entity_add_with_domain(request, domain_name=None,
                           return_view_name='account_profile'):
    if domain_name is None:
        entity = None
    else:
        domain = get_object_or_404(Domain, name=domain_name)
        entity = Entity(domain=domain)
    if request.method == 'POST':
        form = EntityForm(request.user, request.POST, instance=entity)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            messages.success(request, _('Entity created succesfully'))
            if return_view_name == 'entities:edit_metadata':
                url = reverse(return_view_name, args=(instance.id,))
            else:
                url = reverse(return_view_name)
            return HttpResponseRedirect(url)
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))

    else:
        form = EntityForm(request.user, instance=entity)

    return render_to_response('entity/add.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def entity_view(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if entity.has_metadata():
        try:
            revs = add_previous_revisions(entity.metadata.list_revisions())
        except ValueError:
            # New entity with no commited metadata, so revisions are empty
            revs = []
    else:
        revs = []

    return render_to_response('entity/view.html', {
        'entity': entity,
        'revs': revs,
    }, context_instance=RequestContext(request))


@login_required
def entity_remove(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        username = authorname(request.user)
        commit_msg = u'entity removed'
        try:
            ent_md = EntityMD.objects.get(entity=entity)
            AttributesMD.objects.filter(entity_md=ent_md).delete()
            ent_md.delete()
        except EntityMD.DoesNotExist:
            pass
        entity.metadata.delete(username, commit_msg)
        entity.delete()
        messages.success(request, _('Entity removed succesfully'))
        return HttpResponseRedirect(reverse('entities:entities_list'))

    return render_to_response('entity/remove.html', {
        'entity': entity,
    }, context_instance=RequestContext(request))
