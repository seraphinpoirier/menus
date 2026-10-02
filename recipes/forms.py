from django.contrib.auth.models import User
from django import forms

from .models import UserProfile


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