from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template, render_to_string
from django.views import View

from content.forms import UserDetailsForm, CreateProjectForm, DeleteProjectForm, EditProjectForm, CreateScreenForm, \
    EditScreenForm, DeleteScreenForm, CopyScreenForm
from content.models import Prototype, Project, Screen


class IndexView(View):
    template_name = 'content/index.html'
    form_details = UserDetailsForm
    form_password = PasswordChangeForm
    form_delete_project = DeleteProjectForm
    form_rename_project = EditProjectForm

    def get(self, request, *args, **kwargs):
        projects = Project.objects.filter(user=self.request.user).all()

        user = request.user
        return render(request, self.template_name, {'form_details': self.form_details(user,
                                                                                      initial={
                                                                                          'username': user.username,
                                                                                          'email': user.email}),
                                                    'form_password': self.form_password(request.user),
                                                    'projects': projects,
                                                    'form_delete_project': DeleteProjectForm,
                                                    'form_rename_project': EditProjectForm})


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


class ProfileSaveDetailsView(View):
    form_details = UserDetailsForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_details(request.user, request.POST)
        user = request.user
        if form.is_valid():
            response['result'] = True
            form.save()
            msg_html = render_to_string('mail/signing_up.html', {'username': user.username})
            send = send_mail(
                "Смена почты sizze.io",
                msg_html,
                getattr(settings, "EMAIL_HOST_USER"),
                [user.email],
                html_message=msg_html,
                fail_silently=False
            )
            response['send_mail'] = send
        else:
            if request.POST['email'] == user.email:
                response['result'] = True
            if not form.errors.get('username'):
                user.username = request.POST['username']
            else:
                response['result'] = False
                response['errors'] = form.errors
        user.save()
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

            screen = Screen(title='screen#1', project=project, layout=project.prototype.base_layout)
            screen.save()

            response['result'] = True
            response['redirect_url'] = '/'
        else:
            response['result'] = False
            response['errors'] = form.errors
        return JsonResponse(response)


class DeleteProjectView(View):
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


class EditProjectView(View):
    form_class = EditProjectForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            project = Project.objects.filter(user=request.user, pk=form.cleaned_data['id']).first()
            project.name = form.cleaned_data['name']
            project.save()
            response['result'] = True
            response['new_name'] = project.name
            response['id'] = project.id
        else:
            response['result'] = False
            response['errors'] = form.errors
        return JsonResponse(response)


class CopyProjectView(View):
    form_class = DeleteProjectForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            project = Project.objects.filter(user=request.user, pk=form.cleaned_data['project']).first()
            screens = project.screen_set.all()
            project.pk = None
            project.name = f'{project.name}_copy'
            project.save()
            for screen in screens:
                screen.pk = None
                screen.project = project
                screen.save()
            response['result'] = True
            response['html_project'] = render_to_string('content/partials/_project.html', {'project': project})
        else:
            response['result'] = False
        return JsonResponse(response)


class RedactorView(View):
    template_name = 'content/redactor.html'
    form_create_screen = CreateScreenForm
    form_edit_screen = EditScreenForm
    form_copy_screen = CopyScreenForm
    form_delete_screen = DeleteScreenForm

    def get(self, request, project, *args, **kwargs):
        project = get_object_or_404(Project, pk=project, user=request.user)
        screens = project.screen_set.all()
        return render(request, self.template_name, {
            'form_create_screen': self.form_create_screen(initial={'project': project}),
            'form_edit_screen': self.form_edit_screen,
            'form_delete_screen': self.form_delete_screen,
            'form_copy_screen': self.form_copy_screen,
            'screens': screens,

        })


class CreateScreenView(View):
    template_name = 'content/create_project.html'
    form_class = CreateScreenForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            screen = form.save(commit=False)
            screen.user = request.user
            screen.layout = screen.project.prototype.base_layout
            screen.save()
            response['html_screen'] = render_to_string('content/reactor_partials/_screen.html', {'screen': screen})
            response['result'] = True
        else:
            response['result'] = False
            response['errors'] = form.errors
        return JsonResponse(response)


class DeleteScreenView(View):
    form_class = DeleteScreenForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            screen = Screen.objects.filter(pk=form.cleaned_data['screen']).first()
            response['id'] = screen.id
            screen.delete()
            response['result'] = True
        else:
            response['errors'] = form.errors
            response['result'] = False
        return JsonResponse(response)


class EditScreenView(View):
    form_class = EditScreenForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            screen = Screen.objects.filter(pk=form.cleaned_data['id']).first()
            screen.title = form.cleaned_data['title']
            screen.save()
            response['result'] = True
            response['new_name'] = screen.title
            response['id'] = screen.id
        else:
            response['result'] = False
            response['errors'] = form.errors
        return JsonResponse(response)


class CopyScreenView(View):
    form_class = DeleteScreenForm

    def post(self, request, *args, **kwargs):
        response = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            screen = Screen.objects.filter(pk=form.cleaned_data['screen']).first()
            screen.pk = None
            screen.title = f'{screen.title}_copy'
            screen.save()

            response['result'] = True
            response['html_screen'] = render_to_string('content/reactor_partials/_screen.html', {'screen': screen})
        else:
            response['result'] = False
        return JsonResponse(response)


class TestView(View):
    template_name = 'content/test_view.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
