import json
from django.urls import path
from rest_framework import serializers, generics
from rest_framework.views import APIView
from content.models import Screen, Project, Prototype
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from content.models import Project, Category


# router = routers.DefaultRouter()
# router.register(r'screen/<int:id>', ScreenView, basename='screens')


class InitProject(APIView):
    def get(self, request, project, *args, **kwargs):
        response = []
        project = get_object_or_404(Project, pk=project)
        prototype_pk = project.prototype.pk
        categories = Category.objects.filter(categoryprototype__prototype=prototype_pk)
        for category in categories:
            category_j = {}
            category_j['title'] = category.title
            category_j['two_in_row'] = category.two_in_row
            elements = category_j['elements'] = []
            response.append(category_j)
            for element in category.get_elements_on_prototype(prototype_pk).all():
                j_element = {}
                j_element['title'] = element.title
                j_element['layout'] = [element.light_layout, element.dark_layout]
                j_element['image'] = [str(element.light_image), str(element.dark_image)]
                j_element['active'] = element.active
                elements.append(j_element)
        return JsonResponse({'categories': response})


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ['id', 'title', 'layout', 'width', 'height']


class PrototypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prototype
        fields = '__all__'


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
        if payload.get('title'): screen.title = payload['title']
        if payload.get('layout'): screen.layout = payload['layout']
        if payload.get('width'): screen.width = payload['width']
        if payload.get('height'): screen.height = payload['height']
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
            layout="",
            width=project.prototype.width,
            height=project.prototype.height,
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
        screens = project.screen_set.all()
        serializer = ScreenSerializer(screens, many=True)

        return JsonResponse({'result': True, 'screen': serializer.data})


class ProjectApiView(APIView):
    def get(self, request, project_id=None):
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return JsonResponse({'message': 'Project not found', "result": False})
            serializer = ProjectSerializer(project)

        else:
            project = Project.objects.filter(user=request.user).all()
            serializer = ProjectSerializer(project, many=True)

        return JsonResponse({'project': serializer.data})

    def post(self, request):
        payload = json.loads(request.body)
        try:
            prototype = Prototype.objects.get(id=payload['prototype_id'])
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Prototype not found', "result": False})

        project = Project()
        project.prototype = prototype
        project.name = payload['name']
        project.user = request.user
        project.save()
        screen = Screen(
            title='first_page',
            project=project,
            width=project.prototype.width,
            height=project.prototype.height
        )
        screen.save()
        serializer = ProjectSerializer(project)
        data = serializer.data
        data['screen'] = ScreenSerializer(screen).data
        return JsonResponse({'project': data, "result": True})

    def put(self, request, project_id):
        payload = json.loads(request.body)
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        project.name = payload['name']
        project.save()
        serializer = ProjectSerializer(project)
        return JsonResponse({'project': serializer.data, "result": True})

    def delete(self, request, project_id):

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})
        project.delete()
        return JsonResponse({'result': True})


class PrototypeApiView(generics.ListAPIView):
    serializer_class = PrototypeSerializer
    queryset = Prototype.objects.all()


urlpatterns = [
    path('init/<int:project>', InitProject.as_view()),
    path('project', ProjectApiView.as_view()),
    path('project/<int:project_id>', ProjectApiView.as_view()),

    path('prototype', PrototypeApiView.as_view()),

    path('project/<int:project_id>/screens', ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>', ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>/<str:action>', ScreenView.as_view()),
]
