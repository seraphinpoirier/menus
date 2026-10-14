from django.urls import path

from recipes import views

urlpatterns = [
    path("", views.home, name="home"),
    path("generer/", views.generator, name="generator"),
    path("connexion/", views.login_page, name="login"),
    path("inscription/", views.registration_page, name="register"),
    path("profil/", views.profile_page, name="profile"),
    path("repas/", views.meals_page, name="meals"),
    path("deconnexion/", views.logout_page, name="logout"),
    path("ajouter-recette/", views.create_recipe, name="create-recipe"),
    path("api/recipes/", views.recipe_list, name="recipe-list"),
    path(
        "api/meal-frequencies/<int:recipe_id>/",
        views.update_meal_frequency_api,
        name="meal-frequency-update-api",
    ),
    path("api/recipes/search/", views.recipe_search, name="recipe-search"),
    path("api/fixed-meals/", views.set_fixed_meal, name="fixed-meal-set"),
    path(
        "api/fixed-meals/<int:weekday>/<str:meal_type>/",
        views.delete_fixed_meal,
        name="fixed-meal-delete",
    ),
    path("api/weekly-menus/generate/", views.generate_weekly_menu, name="weekly-menu-generate"),
    path(
        "repas/<int:recipe_id>/",
        views.update_meal_frequency,
        name="meal-frequency-update",
    ),
]