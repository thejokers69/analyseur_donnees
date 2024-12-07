# analyse/templatetags/custom_filters.py

from django import template
from django.forms.boundfield import BoundField
from typing import Union, List

register = template.Library()
@register.filter(name='add_class')
def add_class(field, css_class):
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    return field  # Return the field unchanged if it's not a form field
