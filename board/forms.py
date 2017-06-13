from django import forms

from .models import User, Profile
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('required_techs', 'excluded_techs')
