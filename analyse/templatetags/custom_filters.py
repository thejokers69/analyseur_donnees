# analyse/templatetags/custom_filters.py

from django import template
from django.forms.boundfield import BoundField
from typing import Union, List

register = template.Library()

@register.filter(name="add_class")
def add_class(field: BoundField, css_classes: Union[str, List[str]]) -> str:
    """
    Ajoute une ou plusieurs classes CSS à un champ de formulaire sans supprimer les classes existantes.

    :param field: Le champ de formulaire à modifier.
    :param css_classes: Une seule classe sous forme de chaîne ou une liste de classes à ajouter.
    :return: Chaîne HTML du champ avec les classes ajoutées.
    """
    if isinstance(css_classes, str):
        css_classes = css_classes.split()
    existing_classes = field.field.widget.attrs.get('class', '').split()
    new_classes = existing_classes + css_classes
    # Éliminer les doublons tout en préservant l'ordre
    seen = set()
    final_classes = []
    for cls in new_classes:
        if cls not in seen:
            seen.add(cls)
            final_classes.append(cls)
    return field.as_widget(attrs={'class': ' '.join(final_classes)})