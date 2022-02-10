# django-surface-theme

Surface theme is built on top of [Django Dashboard Atlantis Dark](https://appseed.us/admin-dashboards/django-dashboard-atlantis-dark).

## ToDo

`testapp` is a demo app of the theme to cover all customizations and test them. TODO [visual testing](https://github.com/python-needle/needle)?

Package currently needs serious review:

* TESTS!
* every admin template should be reviewed against its core theme peer
* bower takes care of atlantis SCSS but what is minifying/managing javascript files? min versions are out of sync...
* login, logout, ... should replace `admin` templates, instead of requiring adding paths to urls.py - subclass AuthenticationForm instead of custom form as well
* ...
