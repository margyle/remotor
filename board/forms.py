from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.widgets import TextInput

from .models import User, Profile, RequiredKeyword, ExcludedKeyword


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')


class ProfileForm(forms.ModelForm):
    add_required_techs = forms.CharField(max_length=255, required=False)
    add_excluded_techs = forms.CharField(max_length=255, required=False)
    class Meta:
        model = Profile
        fields = ['required_techs',
                  'excluded_techs']
        widgets = {
            'add_required_techs': TextInput(),
            'add_excluded_techs': TextInput(),
            'required_techs': CheckboxSelectMultiple(attrs={"checked":""}),
            'excluded_techs': CheckboxSelectMultiple(attrs={"checked":""}),
        }

    def clean(self, commit=True):
        cleaned_data = self.cleaned_data
        required_techs = self.cleaned_data.get('required_techs', [])
        required_techs += self.cleaned_data.get('add_required_techs', [])
        cleaned_data['required_techs'] = required_techs
        excluded_techs = self.cleaned_data.get('excluded_techs', [])
        excluded_techs += self.cleaned_data.get('add_excluded_techs', [])
        cleaned_data['excluded_techs'] = excluded_techs
        return cleaned_data

    def clean_required_techs(self):
        techs = self.cleaned_data.get('required_techs', '')
        cleaned_techs = []
        for item in techs:
            if not item:
                continue
            obj, _c = RequiredKeyword.objects.get_or_create(name=item.name)
            cleaned_techs.append(obj)
        return cleaned_techs

    def clean_excluded_techs(self):
        techs = self.cleaned_data.get('excluded_techs', '')
        cleaned_techs = []
        for item in techs:
            if not item:
                continue
            obj, _c = ExcludedKeyword.objects.get_or_create(name=item.name)
            cleaned_techs.append(obj)
        return cleaned_techs

    def clean_add_required_techs(self):
        new_techs = self.cleaned_data.get('add_required_techs', '')
        new_techs = [item.strip() for item in new_techs.split(',')]
        cleaned_techs = []
        for item in new_techs:
            if not item:
                continue
            obj, _c = RequiredKeyword.objects.get_or_create(name=item)
            cleaned_techs.append(obj)
        return cleaned_techs

    def clean_add_excluded_techs(self):
        new_techs = self.cleaned_data.get('add_excluded_techs', '')
        new_techs = [item.strip() for item in new_techs.split(',')]
        cleaned_techs = []
        for item in new_techs:
            if not item:
                continue
            obj, _c = ExcludedKeyword.objects.get_or_create(name=item)
            cleaned_techs.append(obj)
        return cleaned_techs
