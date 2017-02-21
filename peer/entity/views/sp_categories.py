
from django.forms import modelformset_factory
from django.shortcuts import render
from peer.entity.models import SPEntityCategory


def manage_categories(request):
    CategoryFormSet = modelformset_factory(SPEntityCategory, fields='__all__')
    if request.method == 'POST':
        formset = CategoryFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            # do something.
    else:
        formset = CategoryFormSet()
    return render(request, 'manage_categories.html', {'formset': formset})
