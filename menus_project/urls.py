from django.urls import path

from recipes import views

urlpatterns = [
    path("", views.home, name="home"),
    path("generer/", views.generator, name="generator"),
    path("connexion/", views.login_page, name="login"),
    path("inscription/", views.registration_page, name="register"),
    path("profil/", views.profile_page, name="profile"),
    path("deconnexion/", views.logout_page, name="logout"),
    path("ajouter-recette/", views.create_recipe, name="create-recipe"),
    path("api/recipes/", views.recipe_list, name="recipe-list"),
    path("api/weekly-menus/generate/", views.generate_weekly_menu, name="weekly-menu-generate"),
]