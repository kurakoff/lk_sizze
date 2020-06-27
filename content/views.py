from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from content.forms import UserDetailsForm, CreateProjectForm, DeleteProjectForm
from content.models import Prototype, Project


class IndexView(View):
    template_name = 'content/index.html'
    form_details = UserDetailsForm
    form_password = PasswordChangeForm
    form_delete_project = DeleteProjectForm

    def get(self, request, *args, **kwargs):
        projects = Project.objects.filter(user=self.request.user).all()

        user = request.user
        return render(request, self.template_name, {'form_details': self.form_details(user,
                                                                                      initial={
                                                                                          'username': user.username,
                                                                                          'email': user.email}),
                                                    'form_password': self.form_password(request.user),
                                                    'projects': projects,
                                                    'form_delete_project': DeleteProjectForm})


class ProfileView(View):
    template_name = 'content/user_profile.html'
    form_password = PasswordChangeForm

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


class CreateProjectView(View):
    template_name = 'content/create_project.html'
    form_class = CreateProjectForm

    def get(self, request, *args, **kwargs):
        prototypes = Prototype.objects.all()
        return render(request, self.template_name, {'prototypes': prototypes, 'form': self.form_class})

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            response['result'] = True
            response['redirect_url'] = '/'
        else:
            response['result'] = False
            response['errors'] = form.errors
        return JsonResponse(response)


class DeleteProject(View):
    form_class = DeleteProjectForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            project = Project.objects.filter(user=request.user, pk=form.cleaned_data['project']).first()
            project.delete()
            response['result'] = True
        else:
            response['result'] = False
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
