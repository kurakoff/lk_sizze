from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
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
        Token.objects.create(user=user)
        return user


class ApiLoginView(APIView):
    permission_classes = ()

    def post(self, request,):
        password = request.data.get("password")
        email = request.data.get("email")
        user = authenticate(username=email, password=password)
        if user:
            response = JsonResponse({"result": True})
            response.set_cookie('token', user.auth_token.key, httponly=True)
            return response
        else:
            return JsonResponse({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

# AUTH URLS


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('users', UserCreate.as_view()),
    path('login', ApiLoginView.as_view()),

    path('create_account/', CreateAccount.as_view(), name='create_account'),
    # Reset password
    path('forgot_password/', CustomPasswordResetView.as_view(), name='forgot_password'),
    path('password_mail_done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_confirm_mail/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset'),
    path('reset_done/', SuccessResetPassword.as_view(), name='password_reset_complete'),
]
