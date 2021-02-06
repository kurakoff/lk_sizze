from rest_framework.permissions import BasePermission
from content.models import ShareProject, Project, ProjectPermissions

message = 'У вас нет на это прав'


class AbstractPermission(BasePermission):
    '''Базовый класс для прав'''

    def __init__(self):
        self.permission = ''

    def has_permission(self, request, view):
        to_all = ShareProject.objects.filter(user=None, project=view.kwargs['project_id'])
        if to_all:
            return bool(request.user)
        try:
            perm = ShareProject.objects.get(user=request.user, project=view.kwargs['project_id'])
            items = perm.permissions.all().values('permission')
            is_read = [self.permission in item['permission'] for item in items]
            return bool(to_all or is_read)
        except:
            pass


class ReadPermission(AbstractPermission):
    '''Проверка права на чтение'''
    message = message

    def __init__(self):
        self.permission = 'edit'


class EditPermission(AbstractPermission):
    '''Проверка права на чтение'''

    message = message

    def __init__(self):
        self.permission = 'read'


class DeletePermission(AbstractPermission):
    '''Проверка права на чтение'''
    message = message

    def __init__(self):
        self.permission = 'delete'


class IsAuthor(BasePermission):
    '''Проверка права на авторство проекта'''
    message = message

    def has_permission(self, request, view):
        try:
            return Project.objects.get(id=view.kwargs['project_id'], user=request.user)
        except:
            pass
