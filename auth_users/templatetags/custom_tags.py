from django import template
from django.core.paginator import Paginator
from django.urls import reverse

from content.models import Element

register = template.Library()


@register.filter(name='add_classes')
def add_classes(value, arg):
    '''
    Add provided classes to form field
    :param value: form field
    :param arg: string of classes seperated by ' '
    :return: edited field
    '''
    css_classes = value.field.widget.attrs.get('class', '')
    # check if class is set or empty and split its content to list (or init list)
    if css_classes:
        css_classes = css_classes.split(' ')
    else:
        css_classes = []
    # prepare new classes to list
    args = arg.split(' ')
    for a in args:
        if a not in css_classes:
            css_classes.append(a)
    # join back to single string
    return value.as_widget(attrs={'class': ' '.join(css_classes)})


LIMIT_SHOW_MORE = 3


@register.filter(name='get_elements_on_prototype')
def get_elements_on_prototype(category, prototype_pk):
    elements = Element.objects.filter(category_prototype__category=category.id,
                                      category_prototype__prototype=prototype_pk)
    paginator_elements = Paginator(elements, LIMIT_SHOW_MORE)
    page1 = paginator_elements.page(1)
    return {'elements': page1.object_list,
            'has_next': page1.has_next()}


@register.filter(name='two_in_row')
def two_in_row(data_element):
    new_data_element = data_element
    elements = data_element['elements'][:]
    new_data_element['elements'] = [[]]

    for i in range(0, len(elements)):
        if len(new_data_element['elements'][-1]) == 2:
            new_data_element['elements'].append([])
        new_data_element['elements'][-1].append(elements[i])
    return new_data_element
