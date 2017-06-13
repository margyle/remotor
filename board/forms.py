from django import forms
from .models import User, Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('required_techs', 'excluded_techs')