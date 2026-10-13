from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FixedMeal, MealFrequency, Recipe


class FixedMealTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.user = get_user_model().objects.create_user("fixed", password="pw")
		cls.recipes = [Recipe.objects.create(name=f"Plat fixe {i}") for i in range(20)]
		cls.soup = Recipe.objects.create(name="Soupe fixe")

	def test_anonymous_cannot_pin_or_search(self):
		response = self.client.post(reverse("fixed-meal-set"), {})
		self.assertEqual(response.status_code, 401)
		self.assertEqual(self.client.get(reverse("recipe-search")).status_code, 401)

	def test_search_filters_by_name(self):
		self.client.force_login(self.user)
		data = self.client.get(reverse("recipe-search"), {"q": "soupe"}).json()
		self.assertIn("Soupe fixe", [r["name"] for r in data])
		self.assertTrue(all("soupe" in r["name"].lower() for r in data))

	def test_pin_replace_and_remove(self):
		self.client.force_login(self.user)
		payload = {"weekday": 6, "meal_type": "lunch", "recipe_id": self.soup.id}
		self.assertEqual(self.client.post(reverse("fixed-meal-set"), payload).status_code, 200)
		payload["recipe_id"] = self.recipes[0].id
		self.client.post(reverse("fixed-meal-set"), payload)
		self.assertEqual(FixedMeal.objects.get().recipe, self.recipes[0])
		url = reverse("fixed-meal-delete", args=[6, "lunch"])
		self.assertEqual(self.client.delete(url).status_code, 200)
		self.assertFalse(FixedMeal.objects.exists())

	def test_invalid_slot_rejected(self):
		self.client.force_login(self.user)
		response = self.client.post(
			reverse("fixed-meal-set"),
			{"weekday": 9, "meal_type": "lunch", "recipe_id": self.soup.id},
		)
		self.assertEqual(response.status_code, 400)

	def test_generation_always_uses_pinned_meal_once(self):
		FixedMeal.objects.create(user=self.user, weekday=6, meal_type="lunch", recipe=self.soup)
		MealFrequency.objects.create(user=self.user, recipe=self.soup, frequency="never")
		self.client.force_login(self.user)
		for _ in range(5):
			days = self.client.get(reverse("weekly-menu-generate")).json()["days"]
			meals = [m for d in days for m in (d["lunch"], d["dinner"])]
			self.assertEqual(len(meals), 14)
			self.assertEqual(days[6]["lunch"]["name"], "Soupe fixe")
			self.assertTrue(days[6]["lunch"]["fixed"])
			self.assertEqual([m["id"] for m in meals].count(self.soup.id), 1)
