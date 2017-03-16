
from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from peer.entity.models import Entity, SPEntityCategory, IdPEntityCategory
from peer.entity.forms import SPEntityCategoryForm, IdPEntityCategoryForm


def manage_sp_categories(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    try:
        sp_categories = entity.sp_categories
    except SPEntityCategory.DoesNotExist:
        sp_categories = SPEntityCategory(entity=entity)
        entity.sp_categories = sp_categories
        sp_categories.save()
    if request.method == 'POST':
        form = SPEntityCategoryForm(request.user, request.POST,
                instance=sp_categories)
        if form.is_valid():
            form.save()
            msg = _('SP categories successfully changed')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('entities:entity_view',
                                         args=(entity_id,)))
    else:
        form = SPEntityCategoryForm(request.user, instance=sp_categories)
    context = {
            'form': form,
            'entity': entity
            }
    return render(request, 'entity/manage_sp_categories.html', context)


def manage_idp_categories(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    try:
        idp_categories = entity.idp_categories
    except IdPEntityCategory.DoesNotExist:
        idp_categories = IdPEntityCategory(entity=entity)
        entity.idp_categories = idp_categories
        idp_categories.save()
    if request.method == 'POST':
        form = IdPEntityCategoryForm(request.user, request.POST,
                instance=idp_categories)
        if form.is_valid():
            form.save()
            msg = _('IdP categories successfully changed')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('entities:entity_view',
                                         args=(entity_id,)))
    else:
        form = IdPEntityCategoryForm(request.user, instance=idp_categories)
    context = {
            'form': form,
            'entity': entity
            }
    return render(request, 'entity/manage_idp_categories.html', context)


