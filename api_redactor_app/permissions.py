from rest_framework.permissions import BasePermission
from content.models import Project, SharedProject
from django.db.models import Q


class IsAuthor(BasePermission):
    '''Проверка права на авторство проекта'''
    message = "Only the author can do this"

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        try:
            if request.user.is_superuser:
                return True
            if Project.objects.get(id=view.kwargs['project_id'], user=request.user):
                return True
        except:
            return False


class BasePermission(BasePermission):
    message = ""
    permission = ""

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        try:
            project = SharedProject.objects.get(Q(to_user=request.user, project=view.kwargs['project_id']) |
                                                Q(all_users=True, project=view.kwargs['project_id']))
            if self.permission in project.permission:
                return True
        except:
            return False


class ReadPermission(BasePermission):
    message = "You do not have read permission"
    permission = "read"

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        try:
            project = SharedProject.objects.get(Q(to_user=request.user, project=view.kwargs['project_id']) |
                                                Q(all_users=True, project=view.kwargs['project_id']))
            if (self.permission in project.permission) and (request.method == "GET"):
                return True
        except:
            return False


class EditPermission(BasePermission):
    message = "You do not have edit permission"
    permission = "edit"


class DeletePermission(BasePermission):
    message = "You do not have delete permission"
    permission = "delete"

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        try:
            project = SharedProject.objects.get(Q(to_user=request.user, project=view.kwargs['project_id']) |
                                                Q(all_users=True, project=view.kwargs['project_id']))
            if (self.permission in project.permission) and (request.method == "DELETE"):
                return True
        except:
            return False


class StartPermission(BasePermission):
    message = "Exceeding user rights"

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        user = request.user
        if user.start is True:
            return True
        else:
            return False


class ProfessionalPermission(BasePermission):
    message = "Exceeding user rights"

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        user = request.user
        if user.professional is True:
            return True
        else:
            return False


class TeamPermission(BasePermission):
    message = "Exceeding user rights"

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        user = request.user
        if user.team is True:
            return True
        else:
            return False