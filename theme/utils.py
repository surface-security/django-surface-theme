from collections import OrderedDict
from django.apps.registry import apps
from functools import lru_cache
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import models, router
from django.utils.html import format_html
from django.urls import reverse, resolve, NoReverseMatch
from django.utils.encoding import smart_text
from django.utils.text import capfirst, slugify
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from jsoneditor.forms import JSONEditor


class DefaultAdminListMixin:
    tab = 0

    formfield_overrides = {models.JSONField: {'widget': JSONEditor}}
    
    class Media(JSONEditor.Media):
        # FIXME: fork jsoneditor and support this in a cleaner way...
        js = JSONEditor.Media.js + ('django-jsoneditor/django-jsoneditor-readonly.js',)

    def get_list_display(self, request):
        default_list_display = super(DefaultAdminListMixin, self).get_list_display(request)

        if 'pk' in default_list_display:
            default_list_display.remove('pk')
        default_list_display.insert(0, 'pk') 

        return default_list_display

    def get_list_display_links(self, request, list_display):
        default_list_display_links = super(DefaultAdminListMixin, self).get_list_display_links(request, list_display)
    
        if not default_list_display_links:
            default_list_display_links = ('pk',)
        
        return default_list_display_links

    def get_readonly_fields(self, request, obj=None):
        fields = super(DefaultAdminListMixin, self).get_readonly_fields(request, obj)
        if not obj:
            return fields

        extended_fields = list(fields) + ['reverse']

        return extended_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(DefaultAdminListMixin, self).get_fieldsets(request, obj)
        if not obj:
            return fieldsets

        default_fieldset_fields = fieldsets[0][1]['fields']
        if 'reverse' in default_fieldset_fields: default_fieldset_fields.remove('reverse')

        fieldsets_to_add = (
            (
                'Relationships',
                {
                    'fields': ('reverse',)
                },
            ),
        )
        # keep the same type whatever it is
        return fieldsets + type(fieldsets)(fieldsets_to_add)
            
    def reverse(self, obj):
        reverse_objects = self.get_related_objects([obj])
        return format_html(f'<div>{self.render_reverse_objects(reverse_objects)}</div>')

    def render_reverse_objects(self, reverse_objects, html_result=''):
        for reverse_object in reverse_objects: 
            if not isinstance(reverse_object, list):
                html_result += f'<p class="m-0">{self.tab*"&emsp;"}{reverse_object}</p>'              
            else:
                self.tab += 1
                html_result += self.render_reverse_objects(reverse_object) 

        if self.tab > 0:
            self.tab -= 1

        return html_result
        
    def get_related_objects(self, objs):
        """
        This method is based on ``get_delete_objects`` where all objects related to ``objs`` 
        are returned for deletion. Unlike ``get_delete_objects``, this method should return 
        not only the related objects for deletion but all related objects to ``objs``.        
        """

        try:
            obj = objs[0]
        except IndexError:
            return []
        else:
            using = router.db_for_read(obj._meta.model)

        collector = admin.utils.NestedObjects(using=using)
        collector.collect(objs)
        
        def format_callback(obj):
            model = obj.__class__
            opts = obj._meta
            no_edit_link = f'{capfirst(opts.verbose_name)}: {obj}'

            try:
                admin_url = reverse(f'admin:{opts.app_label}_{opts.model_name}_change',
                                    None, (admin.utils.quote(obj.pk),))
            except NoReverseMatch:
                # If Change url doesn't exists
                fields = opts.fields

                # Extract the objects from a relationship
                if fields[1].__class__ is models.ForeignKey and fields[2].__class__ is models.ForeignKey:                
                    related_objects = [getattr(obj, fields[1].name), getattr(obj, fields[2].name)]
                    admin_urls = [reverse(f'admin:{related_objects[i]._meta.app_label}_{related_objects[i]._meta.model_name}_change',
                                        None, (admin.utils.quote(related_objects[i].pk),)) for i in range(0,2)]
                    no_edit_link = f'{capfirst(opts.verbose_name)}: {capfirst(fields[1].name)} <a href="{admin_urls[0]}">{related_objects[0]}</a> - {capfirst(fields[2].name)} <a href="{admin_urls[1]}">{related_objects[1]}</a>'

                return no_edit_link

            # Display a link to the admin page.
            return format_html(f'{capfirst(opts.verbose_name)}: <a href="{admin_url}">{obj}</a>')

            # model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}

        return collector.nested(format_callback)

        
def get_app_list(context, order=True):
    admin_site = get_admin_site(context)
    request = context['request']

    app_dict = {}
    for model, model_admin in admin_site._registry.items():
        app_label = model._meta.app_label
        has_module_perms = model_admin.has_module_permission(request)

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                info = (app_label, model._meta.model_name)
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'object_name': model._meta.object_name,
                    'perms': perms,
                    'model_name': model._meta.model_name,
                    'admin_url': reverse(f'admin:{app_label}_{model._meta.model_name}_changelist')
                }

                if perms.get('view', False) or perms.get('change', False):
                    try:
                        model_dict['admin_url'] = reverse(f'admin:{info}_{admin_site.name}_changelist')
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        model_dict['add_url'] = reverse(f'admin:{info}_{admin_site.name}_add')
                    except NoReverseMatch:
                        pass
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    try:
                        name = apps.get_app_config(app_label).verbose_name
                    except NameError:
                        name = app_label.title()
                    app_dict[app_label] = {
                        'name': name,
                        'app_label': app_label,
                        'app_url': reverse(
                            'admin:app_list', kwargs={'app_label': app_label}, current_app=admin_site.name,
                        ),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }

    # Sort the apps alphabetically.
    app_list = list(app_dict.values())
    return app_list


def get_admin_site(context):
    try:
        current_resolver = resolve(context.get('request').path)
        index_resolver = resolve(reverse(f'{current_resolver.namespaces[0]}:index'))

        if hasattr(index_resolver.func, 'admin_site'):
            return index_resolver.func.admin_site

        for func_closure in index_resolver.func.__closure__:
            if isinstance(func_closure.cell_contents, admin.AdminSite):
                return func_closure.cell_contents
    except Exception:
        pass

    return admin.site


def get_model_instance_label(instance):
    if getattr(instance, "related_label", None):
        return instance.related_label()
    return smart_text(instance)


def get_original_menu_items(context):
    pinned_apps = []

    original_app_list = get_app_list(context)

    return map(
        lambda app: {
            'app_label': app['app_label'],
            'url': app['app_url'],
            'url_blank': False,
            'label': app.get('name', capfirst(_(app['app_label']))),
            'has_perms': app.get('has_module_perms', False),
            'models': list(
                map(
                    lambda model: {
                        'url': model.get('admin_url'),
                        'url_blank': False,
                        'name': model['model_name'],
                        'object_name': model['object_name'],
                        'label': model.get('name', model['object_name']),
                        'has_perms': any(model.get('perms', {}).values()),
                    },
                    app['models'],
                )
            ),
            'pinned': app['app_label'] in pinned_apps,
            'custom': False,
        },
        original_app_list,
    )


def get_menu_item_url(url, original_app_list):
    if isinstance(url, dict):
        url_type = url.get('type')

        if url_type == 'app':
            return original_app_list[url['app_label']]['url']
        elif url_type == 'model':
            models = dict(map(lambda x: (x['name'], x['url']), original_app_list[url['app_label']]['models']))
            return models[url['model']]
        elif url_type == 'reverse':
            return reverse(url['name'], args=url.get('args'), kwargs=url.get('kwargs'))
    elif isinstance(url, str):
        return url


def get_menu_items(context):
    original_app_list = OrderedDict(map(lambda app: (app['app_label'], app), get_original_menu_items(context)))
    custom_app_list = settings.SURFACE_MENU_ITEMS

    if custom_app_list not in (None, False):
        if isinstance(custom_app_list, dict):
            admin_site = get_admin_site(context)
            custom_app_list = custom_app_list.get(admin_site.name, [])

        app_list = []

        def get_menu_item_app_model(app_label, data):
            item = {'has_perms': True}

            if 'name' in data:
                parts = data['name'].split('.', 2)

                if len(parts) > 1:
                    app_label, name = parts
                else:
                    name = data['name']

                if app_label in original_app_list:
                    models = dict(map(lambda x: (x['name'], x), original_app_list[app_label]['models']))

                    if name in models:
                        item = models[name].copy()

            if 'label' in data:
                item['label'] = data['label']

            if 'url' in data:
                item['url'] = get_menu_item_url(data['url'], original_app_list)

            if 'url_blank' in data:
                item['url_blank'] = data['url_blank']

            if 'permissions' in data:
                item['has_perms'] = item.get('has_perms', True) and context['user'].has_perms(data['permissions'])

            if 'icon' in data:
                item['icon'] = item.get('icon', 'fas fa-layer-group')

            return item

        def get_menu_item_app(data):
            app_label = data.get('app_label')

            if not app_label:
                if 'label' not in data:
                    raise Exception('Custom menu items should at least have \'label\' or \'app_label\' key')
                app_label = f"custom_{slugify(data['label'], allow_unicode=True)}"

            if app_label in original_app_list:
                item = original_app_list[app_label].copy()
            else:
                item = {'app_label': app_label, 'has_perms': True}

            item['label'] = data.get('label', '')
            item['url_blank'] = data.get('url_blank', '')
            item['icon'] = data.get('icon', 'fas fa-layer-group')

            if 'items' in data:
                item['items'] = list(map(lambda x: get_menu_item_app_model(app_label, x), data['items']))

            if 'url' in data:
                item['url'] = get_menu_item_url(data['url'], original_app_list)

            if 'permissions' in data:
                item['has_perms'] = item.get('has_perms', True) and context['user'].has_perms(data['permissions'])

            return item

        for data in custom_app_list:
            item = get_menu_item_app(data)
            app_list.append(item)

    else:

        def map_item(item):
            item['items'] = item['models']
            return item

        app_list = list(map(map_item, original_app_list.values()))

    current_found = False

    for app in app_list:
        if not current_found:
            for model in app['items']:
                if not current_found and model.get('url') and context['request'].path.startswith(model['url']):
                    model['current'] = True
                    current_found = True
                else:
                    model['current'] = False

            if not current_found and app.get('url') and context['request'].path.startswith(app['url']):
                app['current'] = True
                current_found = True
            else:
                app['current'] = False

    return app_list


def user_is_authenticated(user):
    if not hasattr(user.is_authenticated, '__call__'):
        return user.is_authenticated
    else:
        return user.is_authenticated()


def default_user_avatar(user):
    return staticfiles_storage.url('assets/img/slavatar.png')


@lru_cache
def get_user_avatar_func():
    func_str = getattr(settings, 'THEME_AVATAR_FUNCTION', None)
    if not func_str:
        return default_user_avatar

    import importlib

    mod_str, met_str = func_str.rsplit('.', 1)
    mod = importlib.import_module(mod_str)
    return getattr(mod, met_str)


def get_user_avatar(user):
    return get_user_avatar_func()(user) or default_user_avatar(user)
