import random

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ProfileForm, RecipeForm
from .models import Recipe, UserProfile

WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def home(request):
    context = _profile_context(request)
    return render(request, "index.html", context)


def generator(request):
    context = _profile_context(request)
    return render(request, "generer.html", context)


def _profile_context(request):
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return {"profile": profile}
    return {}


def _safe_next_url(request):
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return target
    return "/"


def _prepare_auth_form(form, registration=False):
    autocomplete = {
        "username": "username",
        "password": "new-password" if registration else "current-password",
        "password1": "new-password",
        "password2": "new-password",
    }
    for name, field in form.fields.items():
        field.widget.attrs["class"] = "form-control"
        if name in autocomplete:
            field.widget.attrs["autocomplete"] = autocomplete[name]


def login_page(request):
    form_data = request.POST if request.method == "POST" else None
    form = AuthenticationForm(request, data=form_data)
    _prepare_auth_form(form)
    next_url = _safe_next_url(request)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(next_url)

    return render(
        request,
        "connexion.html",
        {"form": form, "next_url": next_url, "registration": False},
    )


def registration_page(request):
    form_data = request.POST if request.method == "POST" else None
    form = UserCreationForm(form_data)
    _prepare_auth_form(form, registration=True)
    next_url = _safe_next_url(request)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        UserProfile.objects.create(user=user)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(next_url)

    return render(
        request,
        "connexion.html",
        {"form": form, "next_url": next_url, "registration": True},
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_page(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(
        request.POST or None,
        instance=request.user,
        profile=profile,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("profile")
    return render(request, "profile.html", {"form": form, "profile": profile})


@require_POST
def logout_page(request):
    logout(request)
    return redirect("home")


@require_GET
def recipe_list(request):
    recipes = list(Recipe.objects.values("id", "name", "ingredients", "instructions", "preparation_time", "cooking_time", "servings", "recipe_url", "created_at", "created_by"))
    return JsonResponse(recipes, safe=False)


@require_GET
def generate_weekly_menu(request):
    recipes = list(Recipe.objects.values("id", "name"))
    if len(recipes) < 14:
        return JsonResponse(
            {"error": "Au moins 14 repas sont nécessaires pour générer un menu hebdomadaire."},
            status=400,
        )

    selected_recipes = random.sample(recipes, 14)
    days = [
        {
            "day": weekday,
            "lunch": selected_recipes[index * 2],
            "dinner": selected_recipes[index * 2 + 1],
        }
        for index, weekday in enumerate(WEEKDAYS)
    ]
    return JsonResponse({"days": days})


@login_required
@require_http_methods(["GET", "POST"])
def create_recipe(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = RecipeForm(user=request.user)

    context = _profile_context(request)
    context["form"] = form
    return render(request, "ajouter-recette.html", context)