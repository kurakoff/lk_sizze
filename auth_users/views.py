from django.contrib.auth import login, authenticate
from django.contrib.auth.backends import UserModel
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings

from auth_users.forms import CreateUserForm, LogInForm, ForgotPassword


class LoginView(TemplateView):
    template_name = 'auth/login.html'
    form_class = LogInForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        response = {}

        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            response['result'] = True
            response['redirect_url'] = '/'
        else:
            response['result'] = False
            response['errors'] = {'password': 'username or the password is incorrect',
                                  'email': 'username or the password is incorrect'}
        return JsonResponse(response)


class ForgotPassword(View):
    template_name = 'auth/forgot_password.html'
    form_class = ForgotPassword

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        response = {}
        email = request.POST['email']
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            response['result'] = False
            response['errors'] = {'email': 'user does not exist.'}
            return JsonResponse(response)

        link = 'https://ya.ru'

        msg_html = render_to_string('mail/forgot-password.html', {'link': link})
        send_mail(
            f"Сброс пароля >>>",
            msg_html,
            getattr(settings, "EMAIL_HOST_USER"),
            [user.email],
            html_message=msg_html,
            fail_silently=True
        )
        response['result'] = True
        response['redirect_url'] = '/user/success_reset_mail/'
        return JsonResponse(response)


class CreateAccount(View):
    template_name = 'auth/create_account.html'
    form_class = CreateUserForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        response = {}
        user = User()
        form = self.form_class(request.POST, instance=user)
        try:
            response['result'] = True
            response['redirect_url'] = '/user/login/'
            form.save()

            msg_html = render_to_string('mail/signing_up.html', {'username': user.username})
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
            if form.errors:
                response['errors'] = form.errors
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
