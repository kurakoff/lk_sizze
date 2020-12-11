import json

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import path
from rest_framework import serializers, generics, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .views import (
    LoginView,
    CustomLogoutView,
    CreateAccount,
    # Reset password
    SuccessResetPassword,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        msg_html = render_to_string('mail/signing_up.html', {'username': user.username})
        send_mail(
            f"Добро пожаловать на sizze",
            msg_html,
            getattr(settings, "EMAIL_HOST_USER"),
            [user.email],
            html_message=msg_html,
            fail_silently=True
        )
        return user


class ApiLoginView(APIView):
    permission_classes = ()
    def post(self, request, ):
        password = request.data.get("password")
        email = request.data.get("email")
        user = authenticate(username=email, password=password)
        if user:
            try:
                user.auth_token.delete()
            except Exception as e:
                pass
            Token.objects.create(user=user)
            response = JsonResponse({"result": True, "token": user.auth_token.key})
            response.set_cookie('token', user.auth_token.key, httponly=True)
            return response
        else:
            return JsonResponse({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class UserUpdate(APIView):

    def put(self, request):
        payload = json.loads(request.body)
        user = request.user

        name = payload.get("username")
        email = payload.get("email")

        password_1 = payload.get("password_1")
        password_2 = payload.get("password_2")
        old_password = payload.get("old_password")

        if name:
            user.username = name
        if email:
            user.email = email

        if old_password:
            if user.check_password(old_password) and password_1 == password_2:
                user.set_password(password_1)
            else:
                return JsonResponse({"result": False, 'message': 'Data error'})

        user.save()
        serialize = UserSerializer(user)
        return JsonResponse({"result": True, 'user': serialize.data})


class UserProfile(APIView):

    def get(self, request):
        user = request.user
        serialize = UserSerializer(user)
        return JsonResponse({"result": True, 'user': serialize.data})

# AUTH URLS


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('users', UserCreate.as_view()),

    path('users/change', UserUpdate.as_view()),
    path('users/profile', UserProfile.as_view()),

    path('login', ApiLoginView.as_view()),

    path('create_account/', CreateAccount.as_view(), name='create_account'),
    # Reset password
    path('forgot_password/', CustomPasswordResetView.as_view(), name='forgot_password'),
    path('password_mail_done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_confirm_mail/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset'),
    path('reset_done/', SuccessResetPassword.as_view(), name='password_reset_complete'),
]
