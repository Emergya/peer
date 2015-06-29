from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget

from peer.portal.models import TextChunkModel


class TextChunkAdminForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = TextChunkModel
        fields = "__all__"


class TextChunkAdmin(admin.ModelAdmin):
    form = TextChunkAdminForm
    list_display = ('identifier',)

admin.site.register(TextChunkModel, TextChunkAdmin)
