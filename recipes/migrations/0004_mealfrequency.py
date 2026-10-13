from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
	dependencies = [
		("recipes", "0003_userprofile"),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name="MealFrequency",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				(
					"frequency",
					models.CharField(
						choices=[
							("never", "Jamais"),
							("regular", "Régulier"),
							("very_frequent", "Très fréquent"),
						],
						default="regular",
						max_length=20,
					),
				),
				(
					"recipe",
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="user_frequencies",
						to="recipes.recipe",
					),
				),
				(
					"user",
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name="meal_frequencies",
						to=settings.AUTH_USER_MODEL,
					),
				),
			],
			options={
				"constraints": [
					models.UniqueConstraint(
						fields=("user", "recipe"),
						name="recipes_mealfrequency_user_recipe_unique",
					),
					models.CheckConstraint(
						condition=models.Q(frequency__in=["never", "regular", "very_frequent"]),
						name="recipes_mealfrequency_frequency_valid",
					),
				],
			},
		),
	]
