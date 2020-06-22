from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from auth_users.forms import CreateUserForm
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = 'auth/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ForgotPassword(TemplateView):
    template_name = 'auth/forgot_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CreateAccount(View):
    template_name = 'auth/create_account.html'
    form_class = CreateUserForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        response = {}
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