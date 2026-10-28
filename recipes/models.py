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


class FixedMeal(models.Model):
	class MealType(models.TextChoices):
		LUNCH = "lunch", "Midi"
		DINNER = "dinner", "Soir"

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="fixed_meals",
	)
	weekday = models.PositiveSmallIntegerField()
	meal_type = models.CharField(max_length=10, choices=MealType.choices)
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		related_name="fixed_slots",
	)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=["user", "weekday", "meal_type"],
				name="recipes_fixedmeal_slot_unique",
			),
			models.CheckConstraint(
				condition=models.Q(weekday__gte=0, weekday__lte=6),
				name="recipes_fixedmeal_weekday_valid",
			),
			models.CheckConstraint(
				condition=models.Q(meal_type__in=["lunch", "dinner"]),
				name="recipes_fixedmeal_type_valid",
			),
		]

	def __str__(self):
		return f"{self.user} - {self.weekday}/{self.meal_type}: {self.recipe}"


class SavedMenu(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="saved_menus",
	)
	week_start = models.DateField(verbose_name="Début de semaine (lundi)")
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ["week_start"]
		constraints = [
			models.UniqueConstraint(
				fields=["user", "week_start"],
				name="recipes_savedmenu_user_week_unique",
			),
		]

	def __str__(self):
		return f"{self.user} - semaine du {self.week_start}"


class SavedMenuMeal(models.Model):
	menu = models.ForeignKey(SavedMenu, on_delete=models.CASCADE, related_name="meals")
	weekday = models.PositiveSmallIntegerField()
	meal_type = models.CharField(max_length=10, choices=FixedMeal.MealType.choices)
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="saved_menu_meals")

	class Meta:
		ordering = ["weekday", "meal_type"]
		constraints = [
			models.UniqueConstraint(
				fields=["menu", "weekday", "meal_type"],
				name="recipes_savedmenumeal_slot_unique",
			),
		]


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
