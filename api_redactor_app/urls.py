import json

from django.contrib.auth import authenticate
from django.http import JsonResponse

from django.urls import path
from django.contrib.auth.models import User

from rest_framework import serializers, generics, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from content.models import Screen, Project, Prototype


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
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        if screen_id:
            try:
                screen = project.screen_set.get(id=screen_id)
            except Screen.DoesNotExist:
                return JsonResponse({'message': 'Screen not found', "result": False})

            if action == 'duplicate':
                screen = Screen.objects.filter(id=screen_id, project=project_id).first()
                screen.id = None
                screen.save()
                serializer = ScreenSerializer(screen)
            else:
                serializer = ScreenSerializer(screen)
            return JsonResponse({'screen': serializer.data, "result": True})
        else:
            screens = project.screen_set
            serializer = ScreenSerializer(screens, many=True)
        return JsonResponse({'screens': serializer.data, "result": True})

    def put(self, request, project_id, screen_id=None):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})
        try:
            screen = project.screen_set.get(id=screen_id)
        except Screen.DoesNotExist:
            return JsonResponse({'message': 'Screen not found', "result": False})

        payload = json.loads(request.body)
        if payload['title']:
            screen.title = payload['title']
        if payload['layout']:
            screen.layout = payload['layout']
        screen.save()
        serializer = ScreenSerializer(screen)
        return JsonResponse({'screen': serializer.data, "result": True})

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        payload = json.loads(request.body)
        screen = Screen(
            title=payload['title'],
            project=project,
            layout=project.prototype.base_layout
        )
        screen.save()
        serializer = ScreenSerializer(screen)
        return JsonResponse({'screen': serializer.data, "result": True})

    def delete(self, request, project_id, screen_id=None):

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})
        try:
            screen = project.screen_set.get(id=screen_id)
        except Screen.DoesNotExist:
            return JsonResponse({'message': 'Screen not found', "result": False})

        screen.delete()
        return JsonResponse({'result': True})


class ProjectApiView(APIView):
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})
        serializer = ProjectSerializer(project)
        return JsonResponse({'project': serializer.data})


urlpatterns = [
    path('project/<int:project_id>', ProjectApiView.as_view()),
    path('project/<int:project_id>/screens', ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>', ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>/<str:action>', ScreenView.as_view()),
]
