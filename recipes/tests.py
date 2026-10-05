from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Recipe, UserProfile


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


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_registration_creates_hashed_password_and_signs_user_in(self):
        password = "Saffron!River_2048"

        response = self.client.post(
            reverse("register"),
            {
                "username": "new-member",
                "password1": password,
                "password2": password,
                "next": "https://outside.example/path",
            },
        )

        user = self.user_model.objects.get(username="new-member")
        self.assertRedirects(response, "/")
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_registration_rejects_duplicate_username(self):
        self.user_model.objects.create_user(
            username="existing-member", password="Valid!Password_2048"
        )

        response = self.client.post(
            reverse("register"),
            {
                "username": "existing-member",
                "password1": "Saffron!River_2048",
                "password2": "Saffron!River_2048",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_model.objects.filter(username="existing-member").count(), 1)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(response.context["form"].errors)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-member",
                "password1": "Saffron!River_2048",
                "password2": "Different!River_2048",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user_model.objects.filter(username="new-member").exists())
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(response.context["form"].errors)

    def test_valid_login_authenticates_user_and_keeps_safe_next_path(self):
        password = "Saffron!River_2048"
        user = self.user_model.objects.create_user(username="member", password=password)

        response = self.client.post(
            reverse("login"),
            {"username": "member", "password": password, "next": "/generer/"},
        )

        self.assertRedirects(response, "/generer/", fetch_redirect_response=False)
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    def test_invalid_login_does_not_authenticate_user(self):
        self.user_model.objects.create_user(username="member", password="Saffron!River_2048")

        response = self.client.post(
            reverse("login"),
            {"username": "member", "password": "incorrect-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(response.context["form"].errors)

    def test_login_rejects_external_next_url(self):
        password = "Saffron!River_2048"
        self.user_model.objects.create_user(username="member", password=password)

        response = self.client.post(
            reverse("login"),
            {"username": "member", "password": password, "next": "https://outside.example/path"},
        )

        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_registration_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        registration_url = reverse("register")
        form_response = csrf_client.get(registration_url)
        csrf_token = form_response.cookies["csrftoken"].value

        rejected_response = csrf_client.post(
            registration_url,
            {
                "username": "csrf-member",
                "password1": "Saffron!River_2048",
                "password2": "Saffron!River_2048",
            },
        )
        accepted_response = csrf_client.post(
            registration_url,
            {
                "username": "csrf-member",
                "password1": "Saffron!River_2048",
                "password2": "Saffron!River_2048",
                "csrfmiddlewaretoken": csrf_token,
            },
        )

        self.assertEqual(rejected_response.status_code, 403)
        self.assertRedirects(accepted_response, "/")
        self.assertTrue(self.user_model.objects.filter(username="csrf-member").exists())


class ProfileAndLogoutTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def create_user(self, username="member"):
        return self.user_model.objects.create_user(
            username=username, password="Saffron!River_2048"
        )

    def test_logout_is_post_only_and_requires_csrf(self):
        user = self.create_user()
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(user)
        form_response = csrf_client.get(reverse("home"))
        csrf_token = form_response.cookies["csrftoken"].value

        get_response = csrf_client.get(reverse("logout"))
        self.assertEqual(csrf_client.session.get("_auth_user_id"), str(user.pk))
        rejected_response = csrf_client.post(reverse("logout"))
        self.assertEqual(csrf_client.session.get("_auth_user_id"), str(user.pk))
        accepted_response = csrf_client.post(
            reverse("logout"), {"csrfmiddlewaretoken": csrf_token}
        )

        self.assertEqual(get_response.status_code, 405)
        self.assertEqual(rejected_response.status_code, 403)
        self.assertRedirects(accepted_response, reverse("home"))
        self.assertNotIn("_auth_user_id", csrf_client.session)

    def test_anonymous_profile_visit_redirects_to_login(self):
        response = self.client.get(reverse("profile"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('profile')}",
            fetch_redirect_response=False,
        )

    def test_existing_user_gets_profile_when_opening_profile_page(self):
        user = self.create_user()
        self.client.force_login(user)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_authenticated_user_can_change_username(self):
        user = self.create_user()
        UserProfile.objects.create(user=user)
        self.client.force_login(user)

        response = self.client.post(
            reverse("profile"),
            {"username": "renamed-member", "avatar": UserProfile.Avatar.DEFAULT},
        )

        self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertEqual(user.username, "renamed-member")

    def test_duplicate_username_is_rejected_without_changing_user(self):
        user = self.create_user()
        UserProfile.objects.create(user=user)
        self.create_user(username="taken-name")
        self.client.force_login(user)

        response = self.client.post(
            reverse("profile"),
            {"username": "taken-name", "avatar": UserProfile.Avatar.FIRST},
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["username"])
        self.assertEqual(user.username, "member")
        self.assertEqual(user.profile.avatar, UserProfile.Avatar.DEFAULT)

    def test_each_allowed_avatar_persists(self):
        user = self.create_user()
        UserProfile.objects.create(user=user)
        self.client.force_login(user)

        for avatar in UserProfile.Avatar.values:
            with self.subTest(avatar=avatar):
                response = self.client.post(
                    reverse("profile"), {"username": user.username, "avatar": avatar}
                )

                self.assertRedirects(
                    response, reverse("profile"), fetch_redirect_response=False
                )
                self.assertEqual(UserProfile.objects.get(user=user).avatar, avatar)

    def test_arbitrary_avatar_is_rejected_without_changes(self):
        user = self.create_user()
        UserProfile.objects.create(user=user)
        self.client.force_login(user)

        response = self.client.post(
            reverse("profile"),
            {"username": "changed-member", "avatar": "unapproved.png"},
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["avatar"])
        self.assertEqual(user.username, "member")
        self.assertEqual(user.profile.avatar, UserProfile.Avatar.DEFAULT)

    def test_navigation_varies_with_authentication_and_profile_avatar(self):
        pages = (reverse("home"), reverse("generator"))
        for page in pages:
            with self.subTest(page=page, user="anonymous"):
                response = self.client.get(page)
                self.assertContains(response, f'href="{reverse("login")}"')
                self.assertNotContains(response, "Se déconnecter")
                self.assertNotContains(response, "Modifier mon profil")
                self.assertNotContains(response, "/static/profile_pictures/")

        user = self.create_user()
        UserProfile.objects.create(user=user, avatar=UserProfile.Avatar.SECOND)
        self.client.force_login(user)
        for page in pages:
            with self.subTest(page=page, user="authenticated"):
                response = self.client.get(page)
                self.assertContains(response, "Se déconnecter")
                self.assertContains(response, "Modifier mon profil")
                self.assertContains(
                    response, 'src="/static/profile_pictures/pfp_2.png"'
                )
                self.assertNotContains(response, f'href="{reverse("login")}"')