from django.contrib import admin
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm, ModelLookupForm


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # same as https://github.com/django/django/blob/ca9872905559026af82000e46cde6f7dedc897b6/django/contrib/auth/views.py#L69
                # TODO: ditch all login customization and just overload admin templates -> easier maintenance
                redirect_to = request.POST.get(REDIRECT_FIELD_NAME) or request.GET.get(REDIRECT_FIELD_NAME, "")
                url_is_safe = url_has_allowed_host_and_scheme(
                    url=redirect_to,
                    allowed_hosts=request.get_host(),
                    require_https=request.is_secure(),
                )
                if url_is_safe:
                    return redirect(redirect_to)
                else:
                    return redirect("/")
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(request, "accounts/login.html", {"form": form, "msg": msg, "site_title": admin.site.site_title})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            authenticate(username=username, password=raw_password)

            msg = "User created."
            success = True

            # return redirect("/login/")

        else:
            msg = "Form is not valid"
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


@login_required
def model_lookup_view(request):
    if request.GET:
        result = {"error": False}

        form = ModelLookupForm(request, request.GET)

        if form.is_valid():
            items, total = form.lookup()
            result["items"] = items
            result["total"] = total
        else:
            result["error"] = True

        return JsonResponse(result)
