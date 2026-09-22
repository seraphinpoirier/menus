from django.urls import path

from recipes import views

urlpatterns = [
    path("", views.home, name="home"),
    path("generer/", views.generator, name="generator"),
    path("connexion/", views.login_page, name="login"),
    path("api/recipes/", views.recipe_list, name="recipe-list"),
    path("api/weekly-menus/generate/", views.generate_weekly_menu, name="weekly-menu-generate"),
]