import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Recipe, SavedMenu


class SavedMenuTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user("alice", password="pw12345!")
		self.recipes = [Recipe.objects.create(name=f"Plat test {i}") for i in range(14)]

	def _payload(self):
		days = []
		for weekday in range(7):
			days.append(
				{
					"weekday": weekday,
					"lunch": {"id": self.recipes[weekday * 2].id},
					"dinner": {"id": self.recipes[weekday * 2 + 1].id},
				}
			)
		return json.dumps({"days": days})

	def test_recipe_detail(self):
		response = self.client.get(reverse("recipe-detail", args=[self.recipes[0].id]))
		self.assertEqual(response.json()["name"], "Plat test 0")

	def test_save_requires_login(self):
		response = self.client.post(reverse("weekly-menu-save"), self._payload(), content_type="application/json")
		self.assertEqual(response.status_code, 401)

	def test_save_is_idempotent_per_week_and_listed(self):
		self.client.force_login(self.user)
		for _ in range(2):
			response = self.client.post(reverse("weekly-menu-save"), self._payload(), content_type="application/json")
			self.assertEqual(response.status_code, 200)
		today = timezone.localdate()
		monday = today - timedelta(days=today.weekday())
		self.assertEqual(SavedMenu.objects.filter(user=self.user, week_start=monday).count(), 1)
		page = self.client.get(reverse("saved-menus"))
		self.assertContains(page, "Plat test 0")

	def test_save_rejects_invalid_menu(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse("weekly-menu-save"), '{"days": []}', content_type="application/json")
		self.assertEqual(response.status_code, 400)
