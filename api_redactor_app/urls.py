import json
from django.urls import path
from rest_framework import serializers
from rest_framework.views import APIView

from content.models import Screen, Project, Prototype
from django.http import JsonResponse


# router = routers.DefaultRouter()
# router.register(r'screen/<int:id>', ScreenView, basename='screens')


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ['id', 'title', 'layout']


class PrototypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prototype
        fields = ['device_name', 'base_layout', 'image', 'image_hover']


class ProjectSerializer(serializers.ModelSerializer):
    prototype = PrototypeSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'prototype']


class ScreenView(APIView):

    def get(self, request, project_id, screen_id=None, action=None):
        if not action:
            if screen_id:
                screens = Screen.objects.filter(id=screen_id, project=project_id).first()
                serializer = ScreenSerializer(screens)
            else:
                screens = Screen.objects.filter(project=project_id).all()
                serializer = ScreenSerializer(screens, many=True)
            return JsonResponse({'screens': serializer.data})
        else:
            if action == 'duplicate':
                screen = Screen.objects.filter(id=screen_id, project=project_id).first()
                screen.id = None
                screen.save()
                serializer = ScreenSerializer(screen)
                return JsonResponse({'screen': serializer.data})

    def put(self, request, project_id, screen_id=None):
        if screen_id:
            payload = json.loads(request.body)
            screen = Screen.objects.filter(id=screen_id).first()
            if payload['title']:
                screen.title = payload['title']
            if payload['layout']:
                screen.layout = payload['layout']
            screen.save()
            serializer = ScreenSerializer(screen)
            return JsonResponse({'screen': serializer.data})
        else:
            return JsonResponse({'result': False})

    def post(self, request, project_id, screen_id=None):
        if project_id:
            payload = json.loads(request.body)
            project = Project.objects.get(id=project_id)
            screen = Screen(
                title=payload['title'],
                project=project,
                layout=project.prototype.base_layout
            )
            screen.save()
            serializer = ScreenSerializer(screen)
            return JsonResponse({'screen': serializer.data})
        else:
            return JsonResponse({'result': False})

    def delete(self, request, project_id, screen_id=None):
        if project_id and screen_id:
            screen = Screen.objects.filter(project_id=project_id, id=screen_id).first()
            screen.delete()
            return JsonResponse({'result': True})


class ProjectApiView(APIView):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        serializer = ProjectSerializer(project)
        return JsonResponse({'project': serializer.data})


urlpatterns = [
    path('project/<int:project_id>', ProjectApiView.as_view()),
    path('project/<int:project_id>/screens', ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>', ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>/<str:action>', ScreenView.as_view()),
]
