from django import forms
from django.contrib.auth.models import User

from content.models import Project, Screen


class UserDetailsForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ['email', 'username']

    def save(self, commit=True):
        self.user.username = self.cleaned_data.get('username') or self.username
        self.user.email = self.cleaned_data.get('email') or self.email
        self.user.save()


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'prototype']


class EditProjectForm(forms.Form):
    name = forms.CharField(min_length=1)
    id = forms.IntegerField(widget=forms.HiddenInput)


class CreateScreenForm(forms.ModelForm):
    class Meta:
        model = Screen
        fields = ['title', 'project']


class EditScreenForm(forms.Form):
    title = forms.CharField(min_length=1)
    id = forms.IntegerField(widget=forms.HiddenInput)


class DeleteScreenForm(forms.Form):
    project = forms.IntegerField(widget=forms.HiddenInput)


class DeleteProjectForm(forms.Form):
    project = forms.IntegerField(widget=forms.HiddenInput)
