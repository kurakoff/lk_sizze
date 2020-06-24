from django import forms
from django.contrib.auth.models import User

from content.models import Project


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
