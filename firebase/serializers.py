from content.models import FirebaseSettings, FirebaseRequest
from rest_framework import serializers


class FirebaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseSettings
        fields = '__all__'


class FirebaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseRequest
        fields = '__all__'
