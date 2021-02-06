from rest_framework import serializers
from content.models import ShareProject


class ShareProjectSerializer(serializers.ModelSerializer):
    project = serializers.CharField(read_only=True)

    class Meta:
        model = ShareProject
        fields = ('id', 'permissions', 'project_user_id', 'project', 'user')


class ShareProjectUserSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(read_only=True)
    project_user_id = serializers.IntegerField(read_only=True)
    project = serializers.CharField(read_only=True)

    class Meta:
        model = ShareProject
        fields = ('id', 'permissions', 'project_user_id', 'project', 'user')
