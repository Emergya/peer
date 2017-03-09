from lxml import etree

from django import forms
from django.conf import settings
from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from peer.entity.models import Entity, MDUIdata


def manage_mdui_data(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    initial = [dict(lang=lang[0]) for lang in settings.MDUI_LANGS]
    nlangs = len(initial)
    MDUIdataFormSet = modelformset_factory(MDUIdata,
            fields = ('entity', 'lang', 'display_name', 'description',
                'priv_statement_url', 'information_url'),
            widgets={'lang': forms.TextInput(attrs={'readonly': 'readonly'}),
                     'entity': forms.HiddenInput()},
            max_num=nlangs, validate_max=True,
            min_num=nlangs, validate_min=True)
    # try:
        # mdui_sets = entity.mdui
    # except MDUIdata.DoesNotExist:
        # for lang in settings.MDUI_LANGS:
            # mdui = MDUIdata(entity=entity, lang=lang[0])
            # mdui.save()
        # mdui_sets = entity.mdui
    if request.method == 'POST':
        formset = MDUIdataFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.save()
                entity.modify(etree.tostring(entity._load_metadata().etree,
                    pretty_print=True))
                entity.save()
            msg = _('MDUI data successfully changed')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('entities:entity_view',
                                         args=(entity_id,)))
    else:
        initial = [{'entity': entity, 'lang': lang[0]} for lang in settings.MDUI_LANGS]
        formset = MDUIdataFormSet(initial=initial)
    context = {
            'formset': formset,
            'entity': entity
            }
    return render(request, 'entity/manage_mdui_data.html', context)
