import random

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Recipe

WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def home(request):
    return render(request, "index.html")


def generator(request):
    return render(request, "generer.html")


def login_page(request):
    return render(request, "connexion.html")


@require_GET
def recipe_list(request):
    recipes = list(Recipe.objects.values("id", "name"))
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