import random

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ProfileForm
from .models import MealFrequency, Recipe, UserProfile

WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MEALS_PER_WEEK = 14
VERY_FREQUENT_INCLUSION_RATE = 0.9


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


@login_required
@require_GET
def meals_page(request):
    return render(
        request,
        "repas.html",
        {
            "meals": _get_user_meals(request.user),
            "frequency_choices": MealFrequency.Frequency.choices,
        },
    )


@login_required
@require_POST
def update_meal_frequency(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    frequency = request.POST.get("frequency")
    valid_frequencies = MealFrequency.Frequency.values
    if frequency not in valid_frequencies:
        return render(
            request,
            "repas.html",
            {
                "meals": _get_user_meals(request.user),
                "frequency_choices": MealFrequency.Frequency.choices,
                "frequency_error": "Veuillez choisir une fréquence valide.",
            },
            status=400,
        )

    preference, _ = MealFrequency.objects.get_or_create(
        user=request.user,
        recipe=recipe,
    )
    preference.frequency = frequency
    preference.save(update_fields=["frequency"])
    return redirect("meals")


@require_POST
def logout_page(request):
    logout(request)
    return redirect("home")


@require_GET
def recipe_list(request):
    recipes = list(Recipe.objects.values("id", "name"))
    return JsonResponse(recipes, safe=False)


def _get_user_meals(user):
    preferences = {
        preference.recipe_id: preference
        for preference in MealFrequency.objects.filter(user=user)
    }
    meals = []
    for recipe in Recipe.objects.all():
        preference = preferences.get(recipe.id)
        if preference is None:
            preference = MealFrequency.objects.create(user=user, recipe=recipe)
        meals.append({"recipe": recipe, "preference": preference})
    return meals


@require_POST
def update_meal_frequency_api(request, recipe_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Connectez-vous pour modifier cette préférence."}, status=401)

    recipe = get_object_or_404(Recipe, pk=recipe_id)
    frequency = request.POST.get("frequency")
    if frequency not in MealFrequency.Frequency.values:
        return JsonResponse({"error": "Veuillez choisir une fréquence valide."}, status=400)

    preference, _ = MealFrequency.objects.get_or_create(
        user=request.user,
        recipe=recipe,
    )
    preference.frequency = frequency
    preference.save(update_fields=["frequency"])
    return JsonResponse(
        {"recipe_id": recipe.id, "frequency": preference.frequency}
    )


def _select_recipes(recipes, frequencies, rng=random):
    eligible_recipes = [
        recipe
        for recipe in recipes
        if frequencies.get(recipe["id"], MealFrequency.Frequency.REGULAR)
        != MealFrequency.Frequency.NEVER
    ]
    frequent_recipes = [
        recipe
        for recipe in eligible_recipes
        if frequencies.get(recipe["id"], MealFrequency.Frequency.REGULAR)
        == MealFrequency.Frequency.VERY_FREQUENT
        and rng.random() < VERY_FREQUENT_INCLUSION_RATE
    ]

    if len(frequent_recipes) > MEALS_PER_WEEK:
        selected_recipes = rng.sample(frequent_recipes, MEALS_PER_WEEK)
    else:
        selected_recipes = frequent_recipes
        selected_ids = {recipe["id"] for recipe in selected_recipes}
        remaining_recipes = [
            recipe for recipe in eligible_recipes if recipe["id"] not in selected_ids
        ]
        selected_recipes.extend(
            rng.sample(remaining_recipes, MEALS_PER_WEEK - len(selected_recipes))
        )
    rng.shuffle(selected_recipes)
    return selected_recipes


@require_GET
def generate_weekly_menu(request):
    recipes = list(Recipe.objects.values("id", "name"))
    frequencies = {}
    if request.user.is_authenticated:
        frequencies = dict(
            MealFrequency.objects.filter(user=request.user).values_list(
                "recipe_id", "frequency"
            )
        )
    eligible_count = sum(
        frequencies.get(recipe["id"], MealFrequency.Frequency.REGULAR)
        != MealFrequency.Frequency.NEVER
        for recipe in recipes
    )
    if eligible_count < MEALS_PER_WEEK:
        return JsonResponse(
            {
                "error": (
                    "Il faut au moins 14 repas qui ne sont pas marqués « Jamais » "
                    "pour générer un menu hebdomadaire."
                )
            },
            status=400,
        )

    selected_recipes = _select_recipes(recipes, frequencies)
    for recipe in selected_recipes:
        recipe["frequency"] = frequencies.get(
            recipe["id"], MealFrequency.Frequency.REGULAR
        )
    days = [
        {
            "day": weekday,
            "lunch": selected_recipes[index * 2],
            "dinner": selected_recipes[index * 2 + 1],
        }
        for index, weekday in enumerate(WEEKDAYS)
    ]
    return JsonResponse({"days": days})