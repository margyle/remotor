from django import forms
from .models import User, Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'firstname', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('required_techs', 'excluded_techs')