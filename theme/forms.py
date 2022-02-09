import operator

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q
from functools import reduce
from .utils import user_is_authenticated, get_model_instance_label


try:
    from django.apps import apps

    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"}))


class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password check", "class": "form-control"})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ModelLookupForm(forms.Form):
    app_label = forms.CharField()
    model = forms.CharField()
    q = forms.CharField(required=False)
    page = forms.IntegerField(required=False)
    page_size = forms.IntegerField(required=False, min_value=1, max_value=1000)
    object_id = forms.IntegerField(required=False)
    model_cls = None

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(ModelLookupForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(ModelLookupForm, self).clean()

        if not user_is_authenticated(self.request.user) or not self.request.user.is_staff:
            raise ValidationError('error')

        try:
            self.model_cls = get_model(data['app_label'], data['model'])
        except Exception:
            raise ValidationError('error')

        content_type = ContentType.objects.get_for_model(self.model_cls)
        permission = Permission.objects.filter(content_type=content_type, codename__startswith='view_').first()

        if not self.request.user.has_perm(f"{data['app_label']}.{permission.codename}"):
            raise ValidationError('error')

        return data

    def lookup(self):
        qs = self.model_cls.objects

        if self.cleaned_data['q']:
            if getattr(self.model_cls, 'autocomplete_search_fields', None):
                search_fields = self.model_cls.autocomplete_search_fields()
                filter_data = [Q((field + '__icontains', self.cleaned_data['q'])) for field in search_fields]
                qs = qs.filter(reduce(operator.or_, filter_data)).distinct()
            else:
                qs = qs.none()

        limit = self.cleaned_data['page_size'] or 100
        page = self.cleaned_data['page'] or 1
        offset = (page - 1) * limit

        items = list(
            map(
                lambda instance: {'id': instance.pk, 'text': get_model_instance_label(instance)},
                qs.all()[offset : offset + limit],
            )
        )
        total = qs.count()

        return items, total
