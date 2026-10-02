from django.db import models
from django.conf import settings


class Recipe(models.Model):
	name = models.CharField(max_length=120, unique=True)

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
