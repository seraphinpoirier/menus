from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_test_user(apps, schema_editor):
	User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
	UserProfile = apps.get_model("recipes", "UserProfile")
	database = schema_editor.connection.alias

	user, _ = User.objects.using(database).get_or_create(username="test")
	user.password = make_password("test1234")
	user.save(using=database, update_fields=["password"])
	UserProfile.objects.using(database).get_or_create(user_id=user.pk)


def remove_test_user(apps, schema_editor):
	User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
	User.objects.using(schema_editor.connection.alias).filter(username="test").delete()


class Migration(migrations.Migration):
	dependencies = [
		("recipes", "0005_recipe_preparation_time_recipe_recipe_url"),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.RunPython(create_test_user, remove_test_user),
	]
