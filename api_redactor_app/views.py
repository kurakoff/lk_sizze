from rest_framework import viewsets, status
from .serializers import ShareProjectSerializer, ShareProjectUserSerializer
from rest_framework.response import Response
from content.models import Project, ShareProject, ProjectPermissions
from django.core.exceptions import ObjectDoesNotExist


class ProjectShareView(viewsets.ModelViewSet):
    '''Вьюшка для работы с правами проекта'''

    queryset = ShareProject.objects.all()
    serializer_class = ShareProjectSerializer

    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['project_id'])
        if project:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['project_user_id'] == int(project.user_id):
                try:
                    past_share = ShareProject.objects.get(user=serializer.validated_data['user'])
                    past_share.delete()
                except:
                    pass
                serializer.save(project=project)
            else:
                return Response('Данный юзер не имеет статуса автора проекта', status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response('Проект не найден', status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        share_project = ShareProject.objects.filter(project=kwargs['project_id'])
        if share_project:
            serializer = self.get_serializer(share_project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response('Проект не найден', status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        share_projects = ShareProject.objects.filter(project=kwargs['project_id'])
        if share_project:
            share_projects.delete()
            return Response('Все разрешения на проект удалены', status=status.HTTP_200_OK)
        else:
            return Response('Проект не найден', status=status.HTTP_404_NOT_FOUND)


class ProjectShareToUserView(viewsets.ModelViewSet):
    '''Вьюшка для работы с правами пользователя над проектом'''

    queryset = ShareProject.objects.all()
    serializer_class = ShareProjectUserSerializer

    def get(self, request, *args, **kwargs):
        try:
            share_project_to_user = ShareProject.objects.get(user=kwargs['user'])
            serializer = self.get_serializer(share_project_to_user, many=False)
            if serializer.data:
                return Response(serializer.data, status=status.HTTP_200_OK)
        except ShareProject.DoesNotExist:
            return Response('Этот пользователь не получал права', status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        try:
            share_project = ShareProject.objects.get(user=kwargs['user'])
            permission = ProjectPermissions.objects.all().values('id').order_by('-id')
            if int(request.data['permissions'][0]) <= int(permission[0]['id']):
                serializer = self.get_serializer(share_project, data=request.data)
                if serializer.is_valid():
                    serializer.save()
            else:
                return Response('Права не найдены', status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.data)
        except ShareProject.DoesNotExist:
            return Response('Этот пользователь не получал права', status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        try:
            share_project = ShareProject.objects.get(user=kwargs['user'])
            share_project.delete()
            return Response('Права удалены', status=status.HTTP_200_OK)
        except ShareProject.DoesNotExist:
            return Response('Этот пользователь не получал права', status=status.HTTP_404_NOT_FOUND)
