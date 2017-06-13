from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import TextInput

from .models import User, Profile, RequiredKeyword, ExcludedKeyword


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')


class ProfileForm(forms.ModelForm):
    required_techs = forms.CharField(max_length=255, required=False)
    excluded_techs = forms.CharField(max_length=255, required=False)
    class Meta:
        model = Profile
        fields = ['required_techs',
                  'excluded_techs']
        widgets = {
            'required_techs': TextInput(),
            'excluded_techs': TextInput(),
        }

    def clean_required_techs(self):
        techs = self.cleaned_data.get('required_techs', '')
        techs = [item.strip() for item in techs.split(',')]
        cleaned_techs = []
        for item in techs:
            obj, _c = RequiredKeyword.objects.get_or_create(name=item)
            cleaned_techs.append(obj)
        return cleaned_techs

    def clean_excluded_techs(self):
        techs = self.cleaned_data.get('excluded_techs', '')
        techs = [item.strip() for item in techs.split(',')]
        cleaned_techs = []
        for item in techs:
            obj, _c = ExcludedKeyword.objects.get_or_create(name=item)
            cleaned_techs.append(obj)
        return cleaned_techs
