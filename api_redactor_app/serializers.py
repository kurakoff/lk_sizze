from rest_framework import serializers
from content.models import Screen, Prototype, Project, UserElement, SharedProject


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ['id', 'title', 'layout', 'width', 'height', 'background_color', 'position']


class PrototypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prototype
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    prototype = PrototypeSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'prototype', 'colors']


class OtherProjectSerializer(serializers.ModelSerializer):
    prototype = PrototypeSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'prototype', 'colors']


class UserElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserElement
        fields = ['id', 'title', 'layout']


class ShareProjectBaseSerializer(serializers.ModelSerializer):
    permission = serializers.JSONField(required=True)

    class Meta:
        model = SharedProject
        fields = ['id', 'from_user', 'to_user', 'project', 'permission', 'all_users']
        extra_kwargs = {
            "from_user": {"read_only": True},
            "project": {"read_only": True},
            "to_user": {"required": True},
            "all_users": {"required": False}
            }

    def validate(self, attrs):
        permissions = attrs.get('permission')
        all_users = attrs.get('all_users')
        to_user = attrs.get('to_user')
        base_perm = ['read', 'edit', 'delete']
        if permissions and (all_users is True or to_user is not None):
            for permission in permissions:
                if permission not in base_perm:
                    raise serializers.ValidationError(permission + " is not correct")
        else:
            raise serializers.ValidationError(str(permissions) + " is not correct")
        return attrs


class ShareProjectSerializer(ShareProjectBaseSerializer):

    def to_representation(self, instance):
        rep = super(ShareProjectSerializer, self).to_representation(instance)
        rep['project'] = instance.project.name
        return rep


class SharedProjectDeleteUserSerializer(serializers.Serializer):
    to_user = serializers.EmailField(required=False)
    all_users = serializers.BooleanField(required=False)


class PastProjectsSerializer(serializers.Serializer):
    serialized_data = serializers.JSONField()