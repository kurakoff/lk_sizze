from django.contrib.auth.models import User
from django.forms import ModelForm


class CreateUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

# class LogInForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'password']
