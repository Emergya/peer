from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def get_binding_short(string):
        splited_string = string.split(':')
        return splited_string[-1]


@register.filter
@stringfilter
def get_path(string):
        splited_string = string.split('/')
        return splited_string[-2]
