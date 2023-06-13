import django
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path
from . import views


def custom_page_not_found(request):
    return django.views.defaults.page_not_found(request, None)


def custom_server_error(request):
    return django.views.defaults.server_error(request)


urlpatterns = [
    # Auth
    path("login/", views.login_view, name="login"),
    path("register/", views.register_user, name="register"),
    path("logout/", LogoutView.as_view(extra_context={"site_title": admin.site.site_title}), name="logout"),
    # Model Lookup
    re_path(r"^model_lookup/$", views.model_lookup_view, name="model_lookup"),
    # Testing Pages
    path("test-404/", custom_page_not_found),
    path("test-500/", custom_server_error),
]
