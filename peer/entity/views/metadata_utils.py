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

from peer.entity.forms import EditMetarefreshForm
from peer.entity.forms import EditMonitoringPreferencesForm
from peer.entity.models import Entity
from peer.entity.security import can_edit_entity
from peer.entity.utils import is_subscribed, add_subscriber, remove_subscriber


@login_required
def metarefresh_edit(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    if request.method == 'POST':
        form = EditMetarefreshForm(request.POST)
        if form.is_valid():
            entity.metarefresh_frequency = \
                form.cleaned_data['metarefresh_frequency']
            entity.save()
            messages.success(request, _('Metarefresh edited succesfully'))
            return HttpResponseRedirect(reverse('metarefresh_edit',
                                                args=(entity_id,)))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        form = EditMetarefreshForm(instance=entity)

    return render_to_response('entity/edit_metarefresh.html', {
        'entity': entity,
        'form': form,
    }, context_instance=RequestContext(request))


# Monitor endpoints

@login_required
def monitoring_prefs(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)

    initial = {'want_alerts': is_subscribed(entity, request.user)}

    if request.method == 'POST':
        form = EditMonitoringPreferencesForm(request.POST, initial=initial)
        if form.is_valid():
            want_alerts = form.cleaned_data['want_alerts']
            if want_alerts:
                add_subscriber(entity, request.user)
                msg = _("You are subscribed to this entity's alerts")
            else:
                remove_subscriber(entity, request.user)
                msg = _("You are not subscribed anymore to this entity's alerts")
            entity.save()
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('entities:entity_view',
                                                args=(entity_id, )))
        else:
            messages.error(request,
                           _('Please correct the errors indicated below'))
    else:
        form = EditMonitoringPreferencesForm(initial=initial)

    return render_to_response('entity/edit_monitoring_preferences.html', {
        'entity': entity,
        'form': form,
    }, context_instance=RequestContext(request))
