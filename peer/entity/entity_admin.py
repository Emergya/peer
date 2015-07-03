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

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.utils import quote
from django.contrib.admin.views.main import ChangeList
from django.utils.translation import ugettext_lazy

from peer.entity.models import Entity
from peer.entity import views
from peer.entity.adminsite import entities

ENTITY_OP = 0
ENTITY_OP_LABEL = ugettext_lazy('Act as Entity operator')
MD_REGISTRAR = 1
MD_REGISTRAR_LABEL = ugettext_lazy('Act as MD registrar')

class EntitiesChangeList(ChangeList):

    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse('entities:%s_%s_change' % (self.opts.app_label,
                                               self.opts.model_name),
                       args=(quote(pk),),
                       current_app=self.model_admin.admin_site.name)


class PublicEntityAdmin(admin.ModelAdmin):

    list_display = ('__unicode__', 'owner', 'domain', 'state', 'creation_time', 'modification_time')
    list_filter = ('state', 'owner', 'domain__name', 'creation_time')
    delete_selected_confirmation_template = 'entity/delete_selected_confirmation.html'
    search_fields = ('domain__name', 'owner__username')
    show_full_result_count = True

    def __init__(self, model, admin_site,
                 change_list_template='entity/change_list.html'):
        super(PublicEntityAdmin, self).__init__(model, admin_site)
        self.change_list_template = change_list_template

    def get_queryset(self, request):
        if request.user.is_authenticated():
            role = request.session.get('user-role', ENTITY_OP)
            conditions = (Q(owner=request.user)
                        | Q(state='published')
                        | Q(delegates=request.user))
            if role == ENTITY_OP:
                qs = Entity.objects.filter(conditions)
            else:
                qs = Entity.objects.filter(conditions | Q(moderators=request.user))
            return qs
        return Entity.objects.filter(state='published')

    def get_urls(self):
        return []

    def get_changelist(self, request, **kwargs):
        return EntitiesChangeList

    def has_change_permission(self, request, obj=None):
        return True


entities.register(Entity, PublicEntityAdmin)
