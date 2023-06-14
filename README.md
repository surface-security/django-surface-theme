# django-surface-theme

Surface theme is built on top of [Django Dashboard Atlantis Dark](https://appseed.us/admin-dashboards/django-dashboard-atlantis-dark).

[![PyPI version](https://badge.fury.io/py/django-surface-theme.svg)](https://badge.fury.io/py/django-surface-theme)

## Surface Theme variables

Define custom title in `urls.py`:
```
admin.site.site_title = "Surface Security"
```

Define side menu navigation items by adding the following variable in `settings.py`:
```
SURFACE_MENU_ITEMS = [
    {'label': ('Organisation'), 'icon': 'fas fa-building', 'items':[
        {'name': 'auth.user'}
    ]},
    {'label': ('Organisation'), 'app_label': 'auth', 'icon': 'fas fa-building', 'items':[
        {'name': 'user', 'label': 'Custom Label'},
        {'url': 'https://example.com', 'url_blank': True, 'label': 'Custom URL'}
    ]},
]
```

Define home links and items by adding the following variable in `settings.py`:
```
SURFACE_LINKS_ITEMS = [
    {'label': ('Examples'), 'items':[
        {'url': 'https://example.com', 'url_blank': True, 'name': 'Example.com'}
    ]}
]
```
