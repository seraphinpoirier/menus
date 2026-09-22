from django.db import models


class Recipe(models.Model):
	name = models.CharField(max_length=120, unique=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name
