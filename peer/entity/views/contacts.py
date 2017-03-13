from lxml import etree

from django import forms
from django.forms import modelformset_factory
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from peer.entity.models import Entity, ContactPerson


def manage_contact_data(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)

    ContactsFormSet = modelformset_factory(ContactPerson,
            fields = ('entity', 'type', 'email', 'name', 'phone'),
            widgets={'entity': forms.HiddenInput(),
                     'name': forms.TextInput()},
            max_num=3, validate_max=True,
            min_num=3, validate_min=True)


    if request.method == 'POST':
        formset = ContactsFormSet(request.POST,
                queryset=ContactPerson.objects.filter(entity=entity))
        if formset.is_valid():
            for form in formset:
                form.save()
            entity.modify(etree.tostring(entity._load_metadata().etree,
                pretty_print=True))
            entity.save()
            msg = _('Contact data successfully changed')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('entities:entity_view',
                                         args=(entity_id,)))
    else:
        if entity.contact_people.count():
            queryset = ContactPerson.objects.filter(entity=entity)
            formset = ContactsFormSet(queryset=queryset)
        else:
            queryset = ContactPerson.objects.none()
            initial = [{'entity': entity, 'type': t} for t in ('S', 'A', 'T')]
            formset = ContactsFormSet(initial=initial, queryset=queryset)
    context = {
            'formset': formset,
            'entity': entity
            }
    return render(request, 'entity/manage_contact_data.html', context)

