import django
from django.contrib.auth.views import LogoutView
from django.conf.urls import url
from django.urls import path, re_path, include
from . import views


def custom_page_not_found(request):
    return django.views.defaults.page_not_found(request, None)


def custom_server_error(request):
    return django.views.defaults.server_error(request)


urlpatterns = [
    # Auth
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    # Model Lookup
    url(r'^model_lookup/$', views.model_lookup_view, name='model_lookup'),
    # Testing Pages
    path("test-404/", custom_page_not_found),
    path("test-500/", custom_server_error),
]
