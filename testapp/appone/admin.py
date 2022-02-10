from django.contrib import admin
from theme.utils import DefaultAdminListMixin
from . import models


@admin.register(models.Driver)
class DriverAdmin(DefaultAdminListMixin, admin.ModelAdmin):
    # DefaultAdminListMixin should add `ID` (primary key) column
    list_display = ['last_name']


@admin.register(models.Car)
class CarAdmin(DefaultAdminListMixin, admin.ModelAdmin):
    # DefaultAdminListMixin should *move* `plate` (primary key) column to first position
    list_display = ['doors', 'plate']
