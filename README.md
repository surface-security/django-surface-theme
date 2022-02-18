# django-surface-theme

Surface theme is built on top of [Django Dashboard Atlantis Dark](https://appseed.us/admin-dashboards/django-dashboard-atlantis-dark).

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

## ToDo

`testapp` is a demo app of the theme to cover all customizations and test them. TODO [visual testing](https://github.com/python-needle/needle)?

Package currently needs serious review:

* TESTS!
* every admin template should be reviewed against its core theme peer
* bower takes care of atlantis SCSS but what is minifying/managing javascript files? min versions are out of sync...
* login, logout, ... should replace `admin` templates, instead of requiring adding paths to urls.py - subclass AuthenticationForm instead of custom form as well
* ...
