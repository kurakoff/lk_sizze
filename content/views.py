from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from content.forms import UserDetailsForm


class IndexView(TemplateView):
    template_name = 'content/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProfileView(View):
    template_name = 'content/user_profile.html'
    form_details = UserDetailsForm
    form_password = PasswordChangeForm

    def get(self, request, *args, **kwargs):
        user = request.user
        return render(request, self.template_name,
                      {'form_details': self.form_details(user,
                                                         initial={'username': user.username, 'email': user.email}),
                       'form_password': self.form_password(request.user), })

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_password(request.user, request.POST)
        if not form.is_valid():
            response['result'] = False
            response['errors'] = form.errors
            return JsonResponse(response)
        response['result'] = True
        form.save()
        return JsonResponse(response)


class ProfileSaveDetailsView(View):
    form_details = UserDetailsForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_details(request.user, request.POST)
        if not form.is_valid():
            response['result'] = False
            response['errors'] = form.errors
            return JsonResponse(response)
        response['result'] = True
        form.save()
        return JsonResponse(response)
