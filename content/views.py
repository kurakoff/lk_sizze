import os
from pprint import pprint

from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View

from content.forms import UserDetailsForm, CreateProjectForm, DeleteProjectForm, EditProjectForm, CreateScreenForm, \
    EditScreenForm, DeleteScreenForm, CopyScreenForm, EmailSpammerForm
from content.models import Prototype, Project, Screen, Category, Element, Settings
from django.utils.timezone import now
from django.core.paginator import Paginator

from content.utils import separate_by_n

from sizzy_lk.settings import BASE_DIR


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
            msg_html = render_to_string('mail/Welcome.html', {'username': user.username})
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

            screen = Screen(title='screen#1', project=project, layout="")
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
        ids_project_screens = list(Screen.objects.filter(project=project).values_list('pk', flat=True))
        prototype_pk = project.prototype.pk
        categories = Category.objects.filter(categoryprototype__prototype=prototype_pk)

        return render(request, self.template_name, {
            'form_create_screen': self.form_create_screen(initial={'project': project}),
            'form_edit_screen': self.form_edit_screen,
            'form_delete_screen': self.form_delete_screen,
            'form_copy_screen': self.form_copy_screen,
            'screens': screens,
            'project': project,
            'ids_project_screens': ids_project_screens,
            'categories': categories,
            'prototype_pk': prototype_pk,
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
            screen.layout = ""
            screen.save()
            response['html_screen'] = render_to_string('content/reactor_partials/_screen.html', {'screen': screen})
            response['result'] = True
            response['ids_project_screens'] = list(
                Screen.objects.filter(project=screen.project).values_list('pk', flat=True))
            response['id'] = screen.id
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
            project_id = screen.project.id
            response['id'] = screen.id
            screen.delete()
            response['result'] = True
            response['ids_project_screens'] = list(
                Screen.objects.filter(project_id=project_id).values_list('pk', flat=True))
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
            project = screen.project
            screen.last_change = now()
            screen.pk = None
            screen.title = f'{screen.title}_copy'
            screen.save()

            response['result'] = True
            response['ids_project_screens'] = list(Screen.objects.filter(project=project).values_list('pk', flat=True))
            response['html_screen'] = render_to_string('content/reactor_partials/_screen.html', {'screen': screen})
        else:
            response['result'] = False
        return JsonResponse(response)


class ScreenActionView(View):
    # actions:
    # 1) original_screen
    # 2) get_screen
    # 3) save_screen
    # 3) init_screen

    def post(self, request, action, *args, **kwargs):
        response = {}
        project_id = request.POST.get('project_id')
        if project_id:
            project = Project.objects.get(pk=project_id)
        # assert project_id
        if action == 'init_screen':
            screen = Screen.objects.order_by('-last_change').filter(project=project).first()
            if not screen:
                screen = Screen(title='screen#1', project=project, layout="")
                screen.save()
            response['result'] = True
            response['screen_html'] = screen.layout
            response['screen_id'] = screen.id
        if action == 'get_screen':
            screen_id = request.POST.get('screen_id')
            assert int(screen_id) > 0
            screen = Screen.objects.get(pk=int(screen_id))
            response['result'] = True
            response['screen_html'] = screen.layout
            response['screen_id'] = screen.id
        if action == 'original_screen':
            screen_id = request.POST.get('screen_id')
            screen = Screen.objects.get(pk=int(screen_id))
            response['result'] = True
            response['screen_html'] = ""
            response['screen_id'] = screen.id
        if action == 'save_screen':
            screen_id = request.POST.get('screen_id')
            screen = Screen.objects.get(pk=int(screen_id))
            screen.layout = request.POST.get('layout')
            screen.last_change = now()
            screen.save()
            response['result'] = True
        return JsonResponse(response)


class ElementView(View):
    def post(self, request):
        response = {}
        element_id = request.POST.get('element_id')
        element = Element.objects.get(pk=element_id)
        response['result'] = True
        response['layout'] = element.layout
        return JsonResponse(response)


class ElementShowMoreView(View):
    def post(self, request):
        limit_show_more = Settings.objects.get(slug='limit_show_more').value

        response = {}
        category_id = request.POST.get('category_id')
        prototype_id = request.POST.get('prototype_id')
        page = int(request.POST.get('page'))
        element_view = request.POST.get('view')
        last_cont_full = True if request.POST.get('last_cont_full') == 'true' else False
        category = Category.objects.get(pk=category_id)
        elements = Element.objects.filter(category_prototype__category=category.id,
                                          category_prototype__prototype=prototype_id)
        paginator_elements = Paginator(elements, limit_show_more)
        response['hide_button'] = True
        response['result'] = True
        response['view'] = element_view
        if paginator_elements.page(page).has_next():
            more_elements = paginator_elements.page(page + 1)
            if element_view == 'one_in_row':
                response['elements_block'] = render_to_string(
                    'content/reactor_partials/_elements_paginator_one_row.html',
                    {'elements': more_elements.object_list})
            if element_view == 'two_in_row':
                print(last_cont_full, type(last_cont_full))
                if not last_cont_full:
                    last_elem = more_elements.object_list[0]
                    response['last_elem'] = {'id': last_elem.id, 'url': last_elem.image.url}
                    response['elements_block'] = render_to_string(
                        'content/reactor_partials/_elements_paginator_two_row.html',
                        {'elements': separate_by_n(more_elements.object_list[1:])})
                else:
                    response['elements_block'] = render_to_string(
                        'content/reactor_partials/_elements_paginator_two_row.html',
                        {'elements': separate_by_n(more_elements.object_list)})

            response['page'] = page + 1

            if more_elements.has_next():
                response['hide_button'] = False
        return JsonResponse(response)


class TestView(View):
    template_name = 'content/test_view.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class EmailSpammer(View):
    template_name = 'content/create_email.html'
    form_class = EmailSpammerForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def upload_func(self, file):
        with open(os.path.join(BASE_DIR, 'templates/email_spam/spam.html'), 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES['html'])
            from auth_users.utils import send_html_mail
            from django.contrib.auth.models import User
            data = request.FILES['html']
            self.upload_func(data)
            msg_html = render_to_string("email_spam/spam.html")
            if form.cleaned_data['to']:
                send_html_mail(subject=form.cleaned_data['theme'], html_content=msg_html,
                               sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>', recipient_list=[form.cleaned_data['to']])
            if form.cleaned_data['to'] == '':
                user_list = []
                users = User.objects.all().values('email')
                for i in users:
                    user_list.append(i['email'])
                send_html_mail(subject=form.cleaned_data['theme'], html_content=msg_html,
                               sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>', recipient_list=user_list)
        return redirect('/email/')