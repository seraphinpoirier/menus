from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import MealFrequency, Recipe
from .views import _select_recipes


class DeterministicRandom:
    def random(self):
        return 0

    def sample(self, population, count):
        return list(population)[:count]

    def shuffle(self, population):
        return None


class MealFrequencyTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="member", password="test-pass")
        self.client.force_login(self.user)
        self.recipes = list(Recipe.objects.all())

    def test_meals_page_lists_recipes_and_creates_regular_defaults(self):
        response = self.client.get(reverse("meals"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipes[0].name)
        self.assertEqual(
            MealFrequency.objects.filter(user=self.user).count(),
            Recipe.objects.count(),
        )
        self.assertFalse(
            MealFrequency.objects.filter(user=self.user)
            .exclude(frequency=MealFrequency.Frequency.REGULAR)
            .exists()
        )

    def test_meal_frequency_api_updates_only_the_current_users_preference(self):
        other_user = get_user_model().objects.create_user(username="other", password="test-pass")
        recipe = self.recipes[0]

        response = self.client.post(
            reverse("meal-frequency-update-api", args=[recipe.id]),
            {"frequency": MealFrequency.Frequency.NEVER},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["frequency"], MealFrequency.Frequency.NEVER)
        self.assertEqual(
            MealFrequency.objects.get(user=self.user, recipe=recipe).frequency,
            MealFrequency.Frequency.NEVER,
        )
        self.assertFalse(MealFrequency.objects.filter(user=other_user, recipe=recipe).exists())

    def test_meal_frequency_api_rejects_invalid_values(self):
        response = self.client.post(
            reverse("meal-frequency-update-api", args=[self.recipes[0].id]),
            {"frequency": "sometimes"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(MealFrequency.objects.filter(user=self.user).exists())

    def test_meal_frequency_page_saves_a_choice(self):
        recipe = self.recipes[0]

        response = self.client.post(
            reverse("meal-frequency-update", args=[recipe.id]),
            {"frequency": MealFrequency.Frequency.VERY_FREQUENT},
        )

        self.assertRedirects(response, reverse("meals"), fetch_redirect_response=False)
        self.assertEqual(
            MealFrequency.objects.get(user=self.user, recipe=recipe).frequency,
            MealFrequency.Frequency.VERY_FREQUENT,
        )

    def test_meal_frequency_api_requires_authentication(self):
        self.client.logout()
        response = self.client.post(
            reverse("meal-frequency-update-api", args=[self.recipes[0].id]),
            {"frequency": MealFrequency.Frequency.NEVER},
        )

        self.assertEqual(response.status_code, 401)

    def test_meal_frequency_api_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        page_response = csrf_client.get(reverse("meals"))
        csrf_token = page_response.cookies["csrftoken"].value
        api_url = reverse("meal-frequency-update-api", args=[self.recipes[0].id])

        rejected_response = csrf_client.post(
            api_url,
            {"frequency": MealFrequency.Frequency.NEVER},
        )
        accepted_response = csrf_client.post(
            api_url,
            {"frequency": MealFrequency.Frequency.NEVER},
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(rejected_response.status_code, 403)
        self.assertEqual(accepted_response.status_code, 200)

    def test_generated_menu_excludes_meals_marked_never(self):
        excluded_recipe = self.recipes[0]
        MealFrequency.objects.create(
            user=self.user,
            recipe=excluded_recipe,
            frequency=MealFrequency.Frequency.NEVER,
        )

        response = self.client.get(reverse("weekly-menu-generate"))
        selected_ids = {
            meal["id"]
            for day in response.json()["days"]
            for meal in (day["lunch"], day["dinner"])
        }

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(excluded_recipe.id, selected_ids)

    def test_generated_menu_requires_fourteen_meals_not_marked_never(self):
        for recipe in self.recipes[:7]:
            MealFrequency.objects.create(
                user=self.user,
                recipe=recipe,
                frequency=MealFrequency.Frequency.NEVER,
            )

        response = self.client.get(reverse("weekly-menu-generate"))

        self.assertEqual(response.status_code, 400)

    def test_very_frequent_meal_is_included_when_selected_for_inclusion(self):
        recipe_data = [{"id": recipe.id, "name": recipe.name} for recipe in self.recipes]
        frequent_recipe = recipe_data[0]

        selected = _select_recipes(
            recipe_data,
            {frequent_recipe["id"]: MealFrequency.Frequency.VERY_FREQUENT},
            rng=DeterministicRandom(),
        )

        self.assertIn(frequent_recipe, selected)
        self.assertEqual(len(selected), 14)


class MealFrequencyAccessTests(TestCase):
    def test_anonymous_user_is_redirected_from_meals_page(self):
        response = Client().get(reverse("meals"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('meals')}",
            fetch_redirect_response=False,
        )

    def test_generated_menu_shows_frequency_controls_for_authenticated_users(self):
        user = get_user_model().objects.create_user(username="member", password="test-pass")
        client = Client()
        client.force_login(user)

        response = client.get(reverse("generator"))

        self.assertContains(response, "Modifier la fréquence de")
        self.assertContains(response, "very_frequent")
