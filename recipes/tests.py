from django.test import TestCase
from django.urls import reverse

from .models import Recipe


class WeeklyMenuTests(TestCase):
    def test_seeded_database_contains_twenty_recipes(self):
        self.assertEqual(Recipe.objects.count(), 20)

    def test_generation_returns_seven_days_and_fourteen_distinct_recipes(self):
        response = self.client.get(reverse("weekly-menu-generate"))

        self.assertEqual(response.status_code, 200)
        days = response.json()["days"]
        recipe_ids = [recipe["id"] for day in days for recipe in (day["lunch"], day["dinner"])]

        self.assertEqual(len(days), 7)
        self.assertEqual(len(recipe_ids), 14)
        self.assertEqual(len(set(recipe_ids)), 14)

    def test_generation_requires_at_least_fourteen_recipes(self):
        Recipe.objects.all().delete()

        response = self.client.get(reverse("weekly-menu-generate"))

        self.assertEqual(response.status_code, 400)