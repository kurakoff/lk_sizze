from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.template.loader import render_to_string
from .utils import send_html_mail
from .social import google
from sizzy_lk import settings
from content import models
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(required=False)
    plan = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_staff', 'plan')
        extra_kwargs = {'password': {'write_only': True}, 'is_staff': {'read_only': True}}

    def get_plan(self, obj):
        if obj.userpermission.team is True:
            return 'team'
        elif obj.userpermission.professional is True:
            return 'professional'
        else: return 'start'

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        models.UserPermission.objects.create(user=user)
        msg_html = render_to_string('mail/Welcome.html', {'username': user.username})
        send_html_mail(subject="Welcome to sizze.io", html_content=msg_html,
                       sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>', recipient_list=[user.email])
        # send_mail(
        #     f"Добро пожаловать на sizze",
        #     msg_html,
        #     getattr(settings, "EMAIL_HOST_USER"),
        #     [user.email],
        #     html_message=msg_html,
        #     fail_silently=True
        # )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    old_password = serializers.CharField(required=True)
    new_password_1 = serializers.CharField(required=True)
    new_password_2 = serializers.CharField(required=True)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetPinSerializer(serializers.Serializer):
    pin = serializers.CharField(
        min_length=6, max_length=6, write_only=True)

    class Meta:
        fields = ['pin']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password']


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:

            raise AuthenticationFailed('oops, who are you?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']

        return {'user_id': user_id, 'email': email, 'name': name}


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()


class FigmaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FigmaUser
        fields = '__all__'


class UserAboutSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserAbout
        fields = '__all__'