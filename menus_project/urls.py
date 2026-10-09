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
    path("api/recipes/", views.recipe_list, name="recipe-list"),
    path(
        "api/meal-frequencies/<int:recipe_id>/",
        views.update_meal_frequency_api,
        name="meal-frequency-update-api",
    ),
    path("api/weekly-menus/generate/", views.generate_weekly_menu, name="weekly-menu-generate"),
    path(
        "repas/<int:recipe_id>/",
        views.update_meal_frequency,
        name="meal-frequency-update",
    ),
]