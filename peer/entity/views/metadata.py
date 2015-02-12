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

from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _

from peer.entity.forms import MetadataTextEditForm
from peer.entity.forms import MetadataFileEditForm, MetadataRemoteEditForm
from peer.entity.models import Entity
from peer.entity.security import can_edit_entity, can_approve_change


DEFAULT_SAML_META_JS_PLUGINS = ('attributes', 'certs', 'contact', 'info',
                                'location', 'endpoints')


def _get_edit_metadata_form(request, entity, edit_mode, form=None):
    if form is None:
        if edit_mode == 'text':
            if settings.MODERATION_ENABLED:
                if entity.state == 'published':
                    text = entity.metadata.get_revision()
                else:
                    text = entity.temp_metadata
            else:
                text = entity.metadata.get_revision()
            form = MetadataTextEditForm(entity, request.user,
                                        initial={'metadata_text': text})
        elif edit_mode == 'file':
            # XXX siempre vacia, imborrable, required
            form = MetadataFileEditForm(entity, request.user)
        elif edit_mode == 'remote':
            form = MetadataRemoteEditForm(entity, request.user)
    form_action = reverse('%s_edit_metadata' % edit_mode, args=(entity.id, ))

    context_instance = RequestContext(request)
    return render_to_string('entity/simple_edit_metadata.html', {
        'edit': edit_mode,
        'entity': entity,
        'form': form,
        'form_action': form_action,
        'form_id': edit_mode + '_edit_form',
    }, context_instance=context_instance)


def _get_success_message(action):
    if settings.MODERATION_ENABLED and action is not None:
        if 'approve_changes' == action:
            success_message = _('Entity metadata has been modified')
        elif 'submit_changes' == action:
            success_message = _('Entity metadata modification has been submitted for review')
        elif 'discard_changes' == action:
            success_message = _('Entity metadata modifications have been discarded')
    else:
        success_message = _('Entity metadata has been modified')
    return success_message


def _handle_metadata_post(request, form, return_view):
    if form.is_valid():
        if request.is_ajax():
            # validation of metadata and diff calculation
            diff = form.get_diff()
            html = highlight(diff, DiffLexer(), HtmlFormatter(linenos=True))
            return HttpResponse(html.encode(settings.DEFAULT_CHARSET))
        else:
            # after validation and when user has added the commit message
            if 'button_clicked' in request.POST and request.POST['button_clicked'] != '':
                action = request.POST['button_clicked']
            else:
                action = None
            form.save(action)
            messages.success(request, _get_success_message(action))
            return_url = reverse(return_view, args=(form.entity.id, ))
            return HttpResponseRedirect(return_url)
    else:
        messages.error(request, _('Please correct the errors indicated below'))
        if request.is_ajax():
            sorted_errors = {}
            for field, errors in form.errors.items():
                sorted_error_list = []
                for error in errors:
                    if ':ERROR:' in error or ':FATAL:' in error:
                        sorted_error_list.insert(0, error)
                    else:
                        sorted_error_list.append(error)
                sorted_errors[field] = sorted_error_list

            content = render_to_string('entity/validation_errors.html', {
                'errors': sorted_errors,
            }, context_instance=RequestContext(request))
            return HttpResponseBadRequest(content)


@login_required
def text_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = MetadataTextEditForm(entity, request.user, request.POST)
        if settings.MODERATION_ENABLED:
            if 'button_clicked' in request.POST and request.POST['button_clicked'] != '':
                if 'submit_changes' == request.POST['button_clicked']:
                    if not can_edit_entity(request.user, entity):
                        raise PermissionDenied
                if 'approve_changes' == request.POST['button_clicked']:
                    if not can_approve_change(request.user, entity):
                        raise PermissionDenied
                if 'discard_changes' == request.POST['button_clicked']:
                    if not can_approve_change(request.user, entity):
                        raise PermissionDenied
        else:
            if not can_edit_entity(request.user, entity):
                        raise PermissionDenied
        result = _handle_metadata_post(request, form, 'text_edit_metadata')
        if result is not None:
            return result
    else:
        form = None
    return edit_metadata(request, entity.id, text_form=form,
                         edit_mode='text')


@login_required
def file_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = MetadataFileEditForm(entity, request.user,
                                    request.POST, request.FILES)
        if settings.MODERATION_ENABLED:
            if 'button_clicked' in request.POST and request.POST['button_clicked'] != '' and len(request.FILES) > 0:
                if 'submit_changes' == request.POST['button_clicked']:
                    if not can_edit_entity(request.user, entity):
                        raise PermissionDenied
                if 'approve_changes' == request.POST['button_clicked']:
                    if not can_approve_change(request.user, entity):
                        raise PermissionDenied
                if 'discard_changes' == request.POST['button_clicked']:
                    if not can_approve_change(request.user, entity):
                        raise PermissionDenied
        else:
            if not can_edit_entity(request.user, entity):
                        raise PermissionDenied
        result = _handle_metadata_post(request, form, 'file_edit_metadata')
        if result is not None:
            return result
    else:
        form = None
    return edit_metadata(request, entity.id, edit_mode='upload',
                         file_form=form)


@login_required
def remote_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = MetadataRemoteEditForm(entity, request.user, request.POST)
        if settings.MODERATION_ENABLED:
            if 'button_clicked' in request.POST and request.POST['button_clicked'] != '' and len(request.FILES) > 0:
                if 'submit_changes' == request.POST['button_clicked']:
                    if not can_edit_entity(request.user, entity):
                        raise PermissionDenied
                if 'approve_changes' == request.POST['button_clicked']:
                    if not can_approve_change(request.user, entity):
                        raise PermissionDenied
                if 'discard_changes' == request.POST['button_clicked']:
                    if not can_approve_change(request.user, entity):
                        raise PermissionDenied
        else:
            if not can_edit_entity(request.user, entity):
                        raise PermissionDenied
        result = _handle_metadata_post(request, form, 'remote_edit_metadata')
        if result is not None:
            return result
    else:
        form = None

    return edit_metadata(request, entity.id, edit_mode='remote',
                         remote_form=form)


@login_required
def edit_metadata(request, entity_id, edit_mode='text',
                  text_form=None, file_form=None, remote_form=None):
    entity = get_object_or_404(Entity, id=entity_id)
    if not can_edit_entity(request.user, entity):
        raise PermissionDenied

    samlmetajs_plugins = getattr(settings, 'SAML_META_JS_PLUGINS',
                                 DEFAULT_SAML_META_JS_PLUGINS)

    return render_to_response('entity/edit_metadata.html', {
        'entity': entity,
        'text_html': _get_edit_metadata_form(request, entity, 'text',
                                             form=text_form),
        'file_html': _get_edit_metadata_form(request, entity, 'file',
                                             form=file_form),
        'remote_html': _get_edit_metadata_form(request, entity, 'remote',
                                               form=remote_form),
        'edit_mode': edit_mode,
        'samlmetajs_plugins': samlmetajs_plugins,
        'needs_google_maps': 'location' in samlmetajs_plugins,
    }, context_instance=RequestContext(request))

