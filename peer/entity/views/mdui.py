from lxml import etree

from django import forms
from django.forms import modelformset_factory
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from peer.account.templatetags.account import authorname
from peer.entity.models import Entity, MDUIdata
from peer.entity.utils import write_temp_file


def manage_mdui_data(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)

    MDUIdataFormSet = modelformset_factory(MDUIdata,
            fields = ('entity', 'lang', 'display_name', 'description',
                'priv_statement_url', 'information_url',
                'logo', 'logo_height', 'logo_width'),
            widgets={'lang': forms.TextInput(attrs={'readonly': 'readonly'}),
                     'entity': forms.HiddenInput()},
            max_num=len(settings.MDUI_LANGS), validate_max=True,
            min_num=len(settings.MDUI_LANGS), validate_min=True)

    if request.method == 'POST':
        formset = MDUIdataFormSet(request.POST,
                queryset=MDUIdata.objects.filter(entity=entity))
        if formset.is_valid():
            for form in formset:
                form.save()
            md_str = etree.tostring(entity._load_metadata().etree,
                    pretty_print=True)
            if settings.MODERATION_ENABLED:
                entity.try_to_modify(md_str)
            else:
                content = write_temp_file(md_str)
                name = entity.metadata.name
                username = authorname(request.user)
                commit_msg = 'Saving MDUI Data'
                entity.metadata.save(name, content, username, commit_msg)
            entity.save()
            msg = _('MDUI data successfully changed')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('entities:entity_view',
                                         args=(entity_id,)))
    else:
        if entity.mdui.count():
            queryset = MDUIdata.objects.filter(entity=entity)
            formset = MDUIdataFormSet(queryset=queryset)
        else:
            queryset = MDUIdata.objects.none()
            initial = [{'entity': entity, 'lang': lang[0]}
                                       for lang in settings.MDUI_LANGS]
            formset = MDUIdataFormSet(initial=initial, queryset=queryset)
    context = {
            'formset': formset,
            'entity': entity
            }
    return render(request, 'entity/manage_mdui_data.html', context)
