from django.contrib.auth.models import User
from django import forms

from .models import Recipe, UserProfile


class RecipeForm(forms.ModelForm):
	class Meta:
		model = Recipe
		fields = ["name", "ingredients", "instructions", "preparation_time", "cooking_time", "servings", "recipe_url"]
		labels = {
			"name": "Nom de la recette",
			"ingredients": "Ingrédients (séparés par des virgules)",
			"instructions": "Instructions de préparation",
			"preparation_time": "Temps de préparation (minutes)",
			"cooking_time": "Temps de cuisson (minutes)",
			"servings": "Nombre de portions",
			"recipe_url": "URL de la recette (facultatif)",
		}
		widgets = {
			"name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
			"ingredients": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Ex: 500g de pâtes, 2 tomates, 1 oignon..."}),
			"instructions": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Décrivez les étapes de préparation..."}),
			"preparation_time": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
			"cooking_time": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
			"servings": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
			"recipe_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://exemple.com/ma-recette", "autocomplete": "off"}),
		}

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop("user", None)
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		recipe = super().save(commit=commit)
		if commit and self.user and self.user.is_authenticated:
			recipe.created_by = self.user
			recipe.save(update_fields=["created_by"])
		return recipe


class ProfileForm(forms.ModelForm):
	avatar = forms.ChoiceField(
		choices=UserProfile.Avatar.choices,
		widget=forms.RadioSelect,
		label="Photo de profil",
	)

	class Meta:
		model = User
		fields = ["username"]

	def __init__(self, *args, profile, **kwargs):
		super().__init__(*args, **kwargs)
		self.profile = profile
		self.fields["username"].label = "Nom d’utilisateur"
		self.fields["username"].widget.attrs.update(
			{"class": "form-control", "autocomplete": "username"}
		)
		self.fields["avatar"].initial = profile.avatar

	def save(self, commit=True):
		user = super().save(commit=commit)
		if commit:
			self.profile.avatar = self.cleaned_data["avatar"]
			self.profile.save(update_fields=["avatar"])
		return user