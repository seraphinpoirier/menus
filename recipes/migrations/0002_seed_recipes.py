from django.db import migrations


RECIPES = [
    "Blanquette de veau",
    "Boeuf bourguignon",
    "Couscous aux legumes",
    "Curry de pois chiches",
    "Dahl de lentilles corail",
    "Gratin dauphinois",
    "Lasagnes aux legumes",
    "Omelette aux champignons",
    "Pates bolognaise",
    "Pizza margherita",
    "Poulet roti et pommes de terre",
    "Quiche lorraine",
    "Ratatouille et riz",
    "Risotto aux champignons",
    "Saumon au four et legumes",
    "Salade cesar",
    "Saucisses lentilles",
    "Soupe de legumes",
    "Tajine de poulet",
    "Tarte aux legumes",
]


def seed_recipes(apps, schema_editor):
    Recipe = apps.get_model("recipes", "Recipe")
    for name in RECIPES:
        Recipe.objects.get_or_create(name=name)


def remove_seed_recipes(apps, schema_editor):
    Recipe = apps.get_model("recipes", "Recipe")
    Recipe.objects.filter(name__in=RECIPES).delete()


class Migration(migrations.Migration):
    dependencies = [("recipes", "0001_initial")]

    operations = [migrations.RunPython(seed_recipes, remove_seed_recipes)]