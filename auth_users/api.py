import os, json, random
from .utils import Util
from .social.backend import PasswordlessAuthBackend
from content import models

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf.urls import url
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, HttpResponsePermanentRedirect
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse

from rest_framework import serializers, generics, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .serializers import \
    ChangePasswordSerializer, \
    SetNewPasswordSerializer, \
    ResetPasswordEmailRequestSerializer, \
    UserSerializer,\
    GoogleSocialAuthSerializer


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


class ChangePassword(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return JsonResponse({"result": False, "message": "Old password is not correct"},
                                    status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get("new_password_1") != serializer.data.get("new_password_2"):
                return JsonResponse({"result": False, "message": "Password mismatch"},
                                    status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password_1"))
            self.object.save()
            response = {
                "result": True,
                "message": "Password updated successfully",
            }
            return JsonResponse(response, status=status.HTTP_200_OK)


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get("email", "")
        try:
            user = User.objects.get(email=email)
        except:
            return Response({"result": False, "failed": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if user:
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id)) #закодированный id
            token = PasswordResetTokenGenerator().make_token(user) #токен
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                "password-reset-confirm", kwargs={'uidb64': uidb64, 'token': token})
            redirect_url = request.data.get("redirect_url", "")
            absurl = "http://"+current_site + relativeLink
            email_body = "Hello, \n Use link below to reset your password  \n" + \
                absurl+"?redirect_url="+redirect_url
            data = {"email_body": email_body, "to_email": user.email,
                    "email_subject": "Reset your passsword"}
            Util.send_email(data)
        return Response({"result": True, "success": "We have sent you a link to reset your password"},
                        status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        redirect_url = request.GET.get("redirect_url")
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + "?token_valid=False")

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + "?token_valid=True&message=CredentialsValid&uidb64=" + uidb64 + "&token=" + token)

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + "?token_valid=False")

            except UnboundLocalError as e:
                return Response({"error": "Token is not valid, please request a new one"},
                                status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"success": True, "message": "Password reset success"}, status=status.HTTP_200_OK)


class GoogleSocialAuthView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleSocialAuthSerializer

    def auth(self, email):
        backend = PasswordlessAuthBackend()
        user = backend.authenticate(email=email)
        try:
            user.auth_token.delete()
        except Exception as e:
            pass
        Token.objects.create(user=user)
        return user

    def generate_username(self, email):

        username = email.split("@")[0]
        if not User.objects.filter(username=username).exists():
            return username
        else:
            random_username = username + str(random.randint(0, 1000))
            return generate_username(random_username)

    def post(self, request):
        """
        POST with "auth_token"
        Send an idtoken as from google to get user information
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = (serializer.validated_data['auth_token'])
        email = data['email']
        name = data['name']
        full_name = name.split()
        queryset = User.objects.filter(email=email)
        if queryset.exists() is False:
            user = User.objects.create_user(email=email, username=self.generate_username(email),
                                            first_name=full_name[0], last_name=full_name[1])
            models.SocialUser.objects.create(user=user, provider='google')
            user.set_unusable_password()
            user.is_verified = True
            user.save()
        user = self.auth(email)
        response = JsonResponse({"result": True, "token": user.auth_token.key})
        response.set_cookie('token', user.auth_token.key, httponly=True)
        return response
