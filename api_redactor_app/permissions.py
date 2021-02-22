from rest_framework.permissions import BasePermission
from content.models import Project, SharedProject
from django.db.models import Q


class IsAuthor(BasePermission):
    '''Проверка права на авторство проекта'''
    message = "Only the author of the project can share it"

    def has_permission(self, request, view):
        try:
            permission = Project.objects.get(id=view.kwargs['project_id'], user=request.user)
            return permission
        except:
            pass


class BasePermission(BasePermission):
    message = ""
    permission = ""

    def has_permission(self, request, view):
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
        try:
            project = SharedProject.objects.get(Q(to_user=request.user, project=view.kwargs['project_id']) |
                                                Q(all_users=True, project=view.kwargs['project_id']))
            if (self.permission in project.permission) and (request.method == "DELETE"):
                return True
        except:
            return False

