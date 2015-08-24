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

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

from peer.entity.models import Entity
from peer.entity.entity_admin import PublicEntityAdmin
from peer.entity.adminsite import entities
from peer.entity.paginator import paginated_list_of_entities
from peer.entity.filters import get_filters
from peer.portal.models import TextChunkModel


def index(request):
    try:
        slogan = TextChunkModel.objects.get(identifier='slogan')
        slogan_text = slogan.text
    except TextChunkModel.DoesNotExist:
        slogan_text = ''

    extra_context = {'user': request.user,
                     'slogan': slogan_text,
                     }

    entity_admin = PublicEntityAdmin(Entity, entities,
                                     change_list_template='portal/index.html')
    return entity_admin.changelist_view(request, extra_context)


@login_required
def remote_user_login(request):
    # The Web Server should handle the authentication for us
    # By having the RemoteUser auth backend enabled everything
    # is managed automatically
    return HttpResponseRedirect(reverse('account_profile'))


def general_conditions(request):
    try:
        gc = TextChunkModel.objects.get(identifier='general conditions')
        gc_text = gc.text
    except TextChunkModel.DoesNotExist:
        gc_text = ''
    return render_to_response('portal/general_conditions.html',
                              {'gc': gc_text},
                              context_instance=RequestContext(request))


def explanation(request):
    try:
        wcdw = TextChunkModel.objects.get(identifier='who can do what')
        wcdw_text = wcdw.text
    except TextChunkModel.DoesNotExist:
        wcdw_text = ''
    return render_to_response('portal/who_can_do_what.html',
                              {'wcdw': wcdw_text},
                              context_instance=RequestContext(request))

