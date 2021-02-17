from rest_framework import serializers
from content.models import Screen, Prototype, Project, UserElement


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ['id', 'title', 'layout', 'width', 'height', 'background_color']


class PrototypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prototype
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    prototype = PrototypeSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'prototype', 'colors']


class UserElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserElement
        fields = ['id', 'title', 'layout']
