from django.db import models
from django.conf import settings
from django.utils import timezone


class Recipe(models.Model):
	name = models.CharField(max_length=120, unique=True, verbose_name="Nom")
	ingredients = models.TextField(verbose_name="Ingrédients", blank=True, default="")
	instructions = models.TextField(verbose_name="Instructions", blank=True, default="")
	preparation_time = models.PositiveIntegerField(
		verbose_name="Temps de préparation (minutes)",
		default=15
	)
	cooking_time = models.PositiveIntegerField(
		verbose_name="Temps de cuisson (minutes)",
		default=30
	)
	servings = models.PositiveIntegerField(
		verbose_name="Nombre de portions",
		default=4
	)
	recipe_url = models.URLField(
		verbose_name="URL de la recette",
		blank=True,
		default=""
	)
	created_at = models.DateTimeField(
		verbose_name="Créé le",
		default=timezone.now
	)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		verbose_name="Créé par"
	)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name


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
