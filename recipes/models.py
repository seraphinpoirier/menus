from django.db import models
from django.conf import settings


class Recipe(models.Model):
	name = models.CharField(max_length=120, unique=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name


class MealFrequency(models.Model):
	class Frequency(models.TextChoices):
		NEVER = "never", "Jamais"
		REGULAR = "regular", "Régulier"
		VERY_FREQUENT = "very_frequent", "Très fréquent"

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="meal_frequencies",
	)
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		related_name="user_frequencies",
	)
	frequency = models.CharField(
		max_length=20,
		choices=Frequency.choices,
		default=Frequency.REGULAR,
	)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=["user", "recipe"],
				name="recipes_mealfrequency_user_recipe_unique",
			),
			models.CheckConstraint(
				condition=models.Q(frequency__in=["never", "regular", "very_frequent"]),
				name="recipes_mealfrequency_frequency_valid",
			),
		]

	def __str__(self):
		return f"{self.user} - {self.recipe}: {self.get_frequency_display()}"


class UserProfile(models.Model):
	class Avatar(models.TextChoices):
		DEFAULT = "pfp_default.png", "Par défaut"
		FIRST = "pfp_1.png", "Portrait 1"
		SECOND = "pfp_2.png", "Portrait 2"

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="profile",
	)
	avatar = models.CharField(max_length=32, choices=Avatar.choices, default=Avatar.DEFAULT)

	class Meta:
		constraints = [
			models.CheckConstraint(
				condition=models.Q(avatar__in=["pfp_default.png", "pfp_1.png", "pfp_2.png"]),
				name="recipes_profile_avatar_valid",
			)
		]

	def __str__(self):
		return f"Profil de {self.user.username}"
