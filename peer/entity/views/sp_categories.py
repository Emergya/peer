
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from peer.entity.models import Entity, SPEntityCategory
from peer.entity.forms import SPEntityCategoryForm


def manage_categories(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    try:
        sp_categories = entity.sp_categories
    except SPEntityCategory.DoesNotExist:
        sp_categories = SPEntityCategory(entity=self)
        self.sp_categories = sp_categories
        sp_categories.save()
    if request.method == 'POST':
        form = SPEntityCategoryForm(request.POST,
                instance=sp_categories)
        if form.is_valid():
            form.save()
    else:
        form = SPEntityCategoryForm(instance=sp_categories)
    context = {
            'form': form,
            'entity': entity
            }
    return render(request, 'entity/manage_categories.html', context)
