from django.contrib.auth import login, authenticate
from django.contrib.auth.backends import UserModel
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, LogoutView
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.defaulttags import url
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings

from auth_users.forms import CreateUserForm, LogInForm, ForgotPasswordForm
from rest_framework.authtoken.models import Token


class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/Reset_password.html'
    email_template_name = 'mail/Reset_password.html'
    html_email_template_name = 'mail/Reset_password.html'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/success_reset_mail_send.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/select_password.html'


class CustomLogoutView(LogoutView):
    next_page = '/user/login'


class LoginView(TemplateView):
    template_name = 'auth/login.html'
    form_class = LogInForm

    def get(self, request, *args, **kwargs):
        response = render(request, self.template_name, {'form': self.form_class})
        response.set_cookie('test', 'test', httponly=True, samesite='strict')
        return response

    def post(self, request, *args, **kwargs):
        response = {}
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user:
            login(request, user, backend='auth_users.auth_helpers.helpers.EmailBackend')
            response['result'] = True
            print(request.GET['next'])
            if request.GET['next']:
                response['redirect_url'] = request.GET['next']
            else:
                response['redirect_url'] = '/'
        else:
            response['result'] = False
            response['errors'] = {'password': 'username or the password is incorrect',
                                  'email': 'username or the password is incorrect'}
        return JsonResponse(response)


class CreateAccount(View):
    template_name = 'auth/create_account.html'
    form_class = CreateUserForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.errors:
            response['errors'] = form.errors
            response['result'] = False
            return JsonResponse(response)
        try:
            user = User.objects.create_user(username=request.POST['username'],
                                            email=request.POST['email'],
                                            password=request.POST['password'])
            login(request, user, backend='auth_users.auth_helpers.helpers.EmailBackend')
            response['result'] = True
            response['redirect_url'] = '/'

            msg_html = render_to_string('mail/Welcome.html', {'username': user.username})
            send_mail(
                f"Какой то загаловок",
                msg_html,
                getattr(settings, "EMAIL_HOST_USER"),
                [user.email],
                html_message=msg_html,
                fail_silently=True
            )
        except Exception as e:
            print(e)
            response['result'] = False

        return JsonResponse(response)


class SuccessResetMailSend(TemplateView):
    template_name = 'auth/success_reset_mail_send.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SelectPassword(TemplateView):
    template_name = 'auth/select_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SuccessResetPassword(TemplateView):
    template_name = 'auth/success_reset_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
