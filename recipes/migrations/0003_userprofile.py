from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


AVATARS = ["pfp_default.png", "pfp_1.png", "pfp_2.png"]


def create_profiles_for_existing_users(apps, schema_editor):
	User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
	UserProfile = apps.get_model("recipes", "UserProfile")
	database = schema_editor.connection.alias
	UserProfile.objects.using(database).bulk_create(
		[UserProfile(user_id=user_id) for user_id in User.objects.using(database).values_list("pk", flat=True)]
	)


class Migration(migrations.Migration):
	dependencies = [
		("recipes", "0002_seed_recipes"),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name="UserProfile",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("avatar", models.CharField(choices=[("pfp_default.png", "Par défaut"), ("pfp_1.png", "Portrait 1"), ("pfp_2.png", "Portrait 2")], default="pfp_default.png", max_length=32)),
				("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
			],
			options={
				"constraints": [
					models.CheckConstraint(condition=models.Q(("avatar__in", AVATARS)), name="recipes_profile_avatar_valid"),
				],
			},
		),
		migrations.RunPython(create_profiles_for_existing_users, migrations.RunPython.noop),
	]