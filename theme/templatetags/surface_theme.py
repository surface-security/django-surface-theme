# https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/

from datetime import timedelta
import re
from functools import lru_cache

from django import template
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import stringfilter
from django.conf import settings
from jsoneditor.forms import JSONEditor
from ..utils import get_app_list, get_menu_items, get_user_avatar

register = template.Library()


@register.simple_tag
def get_page_range(p, number, on_each_side=3, on_ends=2):
    paginator = Paginator(p.object_list, p.per_page)
    return paginator.get_elided_page_range(number=number, on_each_side=on_each_side, on_ends=on_ends)


# Helpful with templates to see what's in an object
@register.filter
def get_field_content(obj, field):
    field_name = field.field['name']

    try:
        obj_field = obj._meta.get_field(field_name)

        if obj_field.__class__ is models.JSONField:
            return {
                'type': 'json',
                'field': JSONEditor().render(
                    field_name, getattr(obj, field_name) or [], attrs={'id': f'id_{field_name}'}
                ),
            }

        elif isinstance(obj_field, models.ForeignKey):
            obj_from_field = getattr(obj, field_name)

            if obj_from_field:
                url = reverse(
                    f'admin:{obj_from_field._meta.app_label}_{obj_from_field._meta.model_name}_change',
                    args=[obj_from_field.pk],
                )
                return {'type': 'urls', 'field': [{'url': url, 'obj': obj_from_field}]}

        elif isinstance(obj_field, models.ManyToManyField):
            objects = getattr(obj, field_name)

            urls = []
            for obj in objects.all():
                url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
                urls.append({'url': url, 'obj': obj})

            return {'type': 'urls', 'field': urls}

        else:
            return {'type': 'field', 'field': field}

    except:
        return {'type': 'field', 'field': field}


@register.filter
def get_fields(obj):
    return dir(obj)


@register.filter
@stringfilter
def strip(value):
    return value.strip()


@lru_cache
def _anchor_re():
    return re.compile(r'[^a-zA-Z0-9\-_]')


@register.filter
@stringfilter
def make_anchor(value):
    return _anchor_re().sub('', value)


@register.simple_tag()
def increment(value):
    value += 1
    return value


@register.simple_tag(takes_context=True)
def surface_get_links(context):
    return getattr(settings, 'SURFACE_LINKS_ITEMS', None)


@register.simple_tag(takes_context=True)
def surface_menu(context):
    return get_menu_items(context)


@register.simple_tag(takes_context=True)
def get_params(context):
    params = ''
    for key, value in context.request.GET.items():
        params += f'{key}={value}&'
    return params


@register.filter
def contains_true(app):
    for item in app['items']:
        if item['has_perms'] == True:
            return 1
    return 0


@register.simple_tag
def surface_stats(period):
    today = timezone.now()

    if period == 'last_24_hours':
        yesterday = today - timedelta(days=1)
        return get_user_model().objects.filter(last_login__gte=yesterday).count()
    elif period == 'last_2_weeks':
        two_weeks_ago = today - timedelta(days=14)
        return get_user_model().objects.filter(last_login__gte=two_weeks_ago).count()
    elif period == 'total':
        return get_user_model().objects.exclude(last_login=None).count()
    return 0


@register.simple_tag(takes_context=True)
def surface_get_models(context):
    return get_app_list(context)


@register.filter
def user_avatar(user):
    return get_user_avatar(user)


@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = None

    if hasattr(value, 'field'):
        css_classes = value.field.widget.attrs.get('class', '').split(' ')

        if css_classes and arg not in css_classes:
            css_classes = f'{css_classes} {arg}'
        return value.as_widget(attrs={'class': css_classes})
