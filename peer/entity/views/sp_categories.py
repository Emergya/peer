
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from peer.entity.models import Entity, SPEntityCategory
from peer.entity.forms import SPEntityCategoryForm


def manage_categories(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = SPEntityCategoryForm(request.POST)
        form.save(commit=False)
        form.entity = entity
        if form.is_valid():
            form.save()
    else:
        form = SPEntityCategoryForm({'entity': entity_id})
    context = {
            'form': form,
            'entity': entity
            }
    return render(request, 'entity/manage_categories.html', context)
