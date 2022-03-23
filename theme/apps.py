from django.apps import AppConfig
from django.contrib.admin import options
from django.db import models
from . import widgets


class SurfaceThemeConfig(AppConfig):
    name = 'theme'
    default_auto_field = 'django.db.models.AutoField'


# cleanest way found to override FORMFIELDs used by admin.ModelAdmin
# FIXME: make input_format use one in settings and/or localized forms
options.FORMFIELD_FOR_DBFIELD_DEFAULTS.update(
    {
        models.DateTimeField: {'widget': widgets.DateTimePickerInput, 'input_formats': ['%Y-%m-%d %H:%M %z']},
        models.DateField: {'widget': widgets.DatePickerInput, 'input_formats': ['%Y-%m-%d']},
    }
)
