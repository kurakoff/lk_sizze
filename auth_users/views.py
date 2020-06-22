from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings

from auth_users.forms import CreateUserForm


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
        user = User()
        form = self.form_class(request.POST, instance=user)
        try:
            response['result'] = True
            response['form_url'] = '/user/login/'
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
