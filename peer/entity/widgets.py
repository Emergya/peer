from django import forms

from django.utils.safestring import SafeData, SafeText, mark_safe

class MetadataWidget(forms.widgets.Textarea):
    def __init__(self, attrs=None):
        attrs = attrs or {}
        md_attrs = {'hidden': ''}
        attrs.update(md_attrs)
        super(MetadataWidget, self).__init__(attrs)  

    def render(self, name, value, attrs=None):
        html = super(MetadataWidget, self).render(name, value, attrs)
        return mark_safe('<div id="samlmetaeditor"></div>' + html)
