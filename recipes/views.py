import json
import random
from datetime import timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ProfileForm, RecipeForm
from .models import FixedMeal, MealFrequency, Recipe, SavedMenu, SavedMenuMeal, UserProfile

WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MEALS_PER_WEEK = 14
VERY_FREQUENT_INCLUSION_RATE = 0.9


def home(request):
    context = _profile_context(request)
    return render(request, "index.html", context)


def generator(request):
    context = _profile_context(request)
    context["has_saved_menus"] = (
        request.user.is_authenticated
        and SavedMenu.objects.filter(user=request.user).exists()
    )
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
    recipes = list(Recipe.objects.values("id", "name", "ingredients", "instructions", "preparation_time", "cooking_time", "servings", "recipe_url", "created_at", "created_by"))
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


def _select_recipes(recipes, frequencies, rng=random, count=MEALS_PER_WEEK):
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

    if len(frequent_recipes) > count:
        selected_recipes = rng.sample(frequent_recipes, count)
    else:
        selected_recipes = frequent_recipes
        selected_ids = {recipe["id"] for recipe in selected_recipes}
        remaining_recipes = [
            recipe for recipe in eligible_recipes if recipe["id"] not in selected_ids
        ]
        selected_recipes.extend(
            rng.sample(remaining_recipes, count - len(selected_recipes))
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

    recipes_by_id = {recipe["id"]: recipe for recipe in recipes}
    slots = {}
    if request.user.is_authenticated:
        for fixed in FixedMeal.objects.filter(user=request.user):
            slots[(fixed.weekday, fixed.meal_type)] = recipes_by_id[fixed.recipe_id]

    fixed_ids = {recipe["id"] for recipe in slots.values()}
    free_slot_count = MEALS_PER_WEEK - len(slots)
    pool = [recipe for recipe in recipes if recipe["id"] not in fixed_ids]
    if free_slot_count > 0:
        eligible_pool = sum(
            frequencies.get(recipe["id"], MealFrequency.Frequency.REGULAR)
            != MealFrequency.Frequency.NEVER
            for recipe in pool
        )
        if eligible_pool < free_slot_count:
            return JsonResponse(
                {
                    "error": (
                        "Il n’y a pas assez de repas disponibles (hors « Jamais » "
                        "et repas fixés) pour compléter le menu."
                    )
                },
                status=400,
            )
        random_recipes = iter(_select_recipes(pool, frequencies, count=free_slot_count))
    else:
        random_recipes = iter([])

    days = []
    for index, weekday in enumerate(WEEKDAYS):
        day = {"day": weekday, "weekday": index}
        for meal_type in ("lunch", "dinner"):
            fixed_recipe = slots.get((index, meal_type))
            recipe = dict(fixed_recipe) if fixed_recipe else next(random_recipes)
            recipe["fixed"] = fixed_recipe is not None
            recipe["frequency"] = frequencies.get(
                recipe["id"], MealFrequency.Frequency.REGULAR
            )
            day[meal_type] = recipe
        days.append(day)
    return JsonResponse({"days": days})


@require_GET
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return JsonResponse(
        {
            "id": recipe.id,
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "preparation_time": recipe.preparation_time,
            "cooking_time": recipe.cooking_time,
            "servings": recipe.servings,
            "recipe_url": recipe.recipe_url,
        }
    )


def _current_week_start():
    today = timezone.localdate()
    return today - timedelta(days=today.weekday())


@require_POST
def save_weekly_menu(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Connectez-vous pour sauvegarder ce menu."}, status=401)
    try:
        days = json.loads(request.body)["days"]
        entries = {}
        for day in days:
            for meal_type in FixedMeal.MealType.values:
                weekday = int(day["weekday"])
                if not 0 <= weekday <= 6:
                    raise ValueError
                entries[(weekday, meal_type)] = int(day[meal_type]["id"])
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"error": "Menu invalide."}, status=400)

    recipes = Recipe.objects.in_bulk(set(entries.values()))
    if len(entries) != MEALS_PER_WEEK or len(recipes) != len(set(entries.values())):
        return JsonResponse({"error": "Menu invalide."}, status=400)

    week_start = _current_week_start()
    with transaction.atomic():
        menu, _ = SavedMenu.objects.get_or_create(user=request.user, week_start=week_start)
        menu.meals.all().delete()
        SavedMenuMeal.objects.bulk_create(
            SavedMenuMeal(menu=menu, weekday=weekday, meal_type=meal_type, recipe=recipes[recipe_id])
            for (weekday, meal_type), recipe_id in entries.items()
        )
    return JsonResponse({"week_start": week_start.isoformat()})


@login_required
@require_GET
def saved_menus_page(request):
    menus = []
    queryset = SavedMenu.objects.filter(user=request.user).prefetch_related("meals__recipe")
    for menu in queryset:
        slots = {(meal.weekday, meal.meal_type): meal.recipe for meal in menu.meals.all()}
        days = [
            {"name": name, "lunch": slots.get((index, "lunch")), "dinner": slots.get((index, "dinner"))}
            for index, name in enumerate(WEEKDAYS)
        ]
        menus.append(
            {
                "week_start": menu.week_start,
                "week_end": menu.week_start + timedelta(days=6),
                "days": days,
            }
        )
    context = _profile_context(request)
    context["menus"] = menus
    return render(request, "menus-sauvegardes.html", context)


@require_GET
def recipe_search(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Connectez-vous pour rechercher un repas."}, status=401)
    query = request.GET.get("q", "").strip()
    recipes = Recipe.objects.filter(name__icontains=query).values("id", "name")[:10]
    return JsonResponse(list(recipes), safe=False)


@require_POST
def set_fixed_meal(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Connectez-vous pour fixer un repas."}, status=401)
    try:
        weekday = int(request.POST.get("weekday", ""))
        recipe_id = int(request.POST.get("recipe_id", ""))
    except ValueError:
        return JsonResponse({"error": "Requête invalide."}, status=400)
    meal_type = request.POST.get("meal_type")
    if not 0 <= weekday <= 6 or meal_type not in FixedMeal.MealType.values:
        return JsonResponse({"error": "Créneau invalide."}, status=400)
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    FixedMeal.objects.update_or_create(
        user=request.user,
        weekday=weekday,
        meal_type=meal_type,
        defaults={"recipe": recipe},
    )
    return JsonResponse({"weekday": weekday, "meal_type": meal_type, "recipe_id": recipe.id})


@require_http_methods(["DELETE"])
def delete_fixed_meal(request, weekday, meal_type):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Connectez-vous pour modifier ce repas."}, status=401)
    FixedMeal.objects.filter(
        user=request.user, weekday=weekday, meal_type=meal_type
    ).delete()
    return JsonResponse({"weekday": weekday, "meal_type": meal_type})


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