import datetime
import random
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
    downloadCount = serializers.SerializerMethodField()
    isVideoExamplesDisabled = serializers.SerializerMethodField()
    promo = serializers.SerializerMethodField()
    copyCount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_staff', 'plan', 'downloadCount', 'isVideoExamplesDisabled',
                  'promo', 'copyCount')
        extra_kwargs = {'password': {'write_only': True}, 'is_staff': {'read_only': True}}

    def get_plan(self, obj):
        permission = {
            "START": 'start',
            "TEAM": 'team',
            "PROFESSIONAL": 'professional',
            "ENTERPRISE": 'enterprise'
            }
        return permission[obj.userpermission.permission]

    def get_copyCount(self, obj):
        return obj.userpermission.copyCount

    def get_promo(self, obj):
        data = ['promocode', 'activate', 'activated', 'discount', 'free_month', 'start_date', 'end_date']
        res = {}
        for value in data:
            res[value] = getattr(obj.promocode, value)
        return res

    def get_downloadCount(self, obj):
        return obj.userpermission.downloadCount

    def get_isVideoExamplesDisabled(self, obj):
        return obj.userpermission.isVideoExamplesDisabled

    def get_promo_code(self, num_chars):
        uniq = False
        while uniq is False:
            code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            code = ''
            for i in range(0, num_chars):
                slice_start = random.randint(0, len(code_chars) - 1)
                code += code_chars[slice_start: slice_start + 1]
            check = models.Promocode.objects.filter(promocode=code)
            if len(check) == 0:
                uniq = True
        return code

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        promo=self.get_promo_code(num_chars=5)
        perm = models.UserPermission.objects.create(user=user)
        promo = models.Promocode.objects.create(user=user, promocode=promo)
        about = models.UserAbout.objects.create(user=user)
        perm.save()
        promo.save()
        about.save()
        msg_html = render_to_string('mail/Welcome.html', {'username': user.username})
        send_html_mail(subject="Welcome to sizze.io", html_content=msg_html,
                       sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>', recipient_list=[user.email])
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


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tasks
        fields = '__all__'


class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnterpriseUser
        fields = '__all__'
