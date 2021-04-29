import json, secrets, string, logging, requests

from django.template.loader import render_to_string

from .social.backend import PasswordlessAuthBackend
from content import models

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import \
    ChangePasswordSerializer, \
    SetNewPasswordSerializer, \
    ResetPasswordEmailRequestSerializer, \
    SetPinSerializer,\
    UserSerializer,\
    GoogleSocialAuthSerializer,\
    EmailLoginSerializer,\
    FigmaUserSerializer


logger = logging.getLogger('django')
auth = logging.getLogger('auth')
figma = logging.getLogger('figma')


class ApiLoginView(APIView):
    permission_classes = [AllowAny]

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
            response = Response()
            response.set_cookie(key='access_token', value=user.auth_token.key, httponly=True, domain=None)
            response.data = {"result": True, "token": user.auth_token.key}
            print(request.COOKIES)
            auth.info("user {} login".format(user))
            return response
        else:
            return JsonResponse({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        auth.info("user create email: {} username: {}".format(request.data['email'], request.data['username']))
        return self.create(request, *args, **kwargs)


class UserUpdate(APIView):

    def put(self, request):
        print(request.COOKIES)
        payload = json.loads(request.body)
        user = request.user

        name = payload.get("username")
        email = payload.get("email")

        password_1 = payload.get("password_1")
        password_2 = payload.get("password_2")
        old_password = payload.get("old_password")

        if name:
            user.username = name
            auth.info("user {} change name {}".format(user, name))
        if email:
            user.email = email
            auth.info("user {} change email {}".format(user, email))

        if old_password:
            if user.check_password(old_password) and password_1 == password_2:
                user.set_password(password_1)
                auth.info("user {} change password".format(user))
            else:
                return JsonResponse({"result": False, 'message': 'Data error'})

        user.save()
        serialize = UserSerializer(user)
        return JsonResponse({"result": True, 'user': serialize.data})


class UserProfile(APIView):

    def get(self, request):
        print(request.COOKIES)
        user = request.user
        serialize = UserSerializer(user)
        return JsonResponse({"result": True, 'user': serialize.data})


class ChangePassword(APIView):

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request):
        print(request.COOKIES)
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        if not self.object.check_password(serializer.data.get("old_password")):
            return JsonResponse({"result": False, "message": "Old password is not correct"},
                                status=status.HTTP_400_BAD_REQUEST)
        if serializer.data.get("new_password_1") != serializer.data.get("new_password_2"):
            return JsonResponse({"result": False, "message": "Password mismatch"},
                                status=status.HTTP_400_BAD_REQUEST)
        self.object.set_password(serializer.data.get("new_password_1"))
        self.object.save()
        auth.info("user {} change password".format(request.user))
        response = {
            "result": True,
            "message": "Password updated successfully",
        }
        return JsonResponse(response, status=status.HTTP_200_OK)


class ResetPasswordEmailView(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = [AllowAny]

    def generate_pin(self):
        alphabet = string.ascii_letters + string.digits
        pin = ''.join(secrets.choice(alphabet) for i in range(6))
        return pin

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except:
            return Response({"result": False, "message": "User with this email does not exist"})
        try:
            reset = models.PasswordReset.objects.filter(to_user=user, activate=False)
            reset.delete()
        except:
            pass
        if user:
            while True:
                reset = models.PasswordReset.objects.create(
                    to_user=user,
                    pin=self.generate_pin(),
                    activate=False
                )
                if reset:
                    reset.save()
                    break
            msg_html = render_to_string('mail/Reset_password.html', {'pin': reset.pin})
            from .utils import send_html_mail
            send_html_mail(subject="Your PIN code to reset your Sizze.io password", html_content=msg_html, sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>',
                           recipient_list=[user.email])
        auth.info("Send reset pin to email {}".format(email))
        return JsonResponse({"result": True, "message": "We have sent you a link to reset your password"},
                            status=status.HTTP_200_OK)


class SetPinView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetPinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pin = request.data.get('pin')
        try:
            reset = models.PasswordReset.objects.get(pin=pin)
            if reset.activate is True:
                return JsonResponse({"result": False, "message": "This pin code is already activated"},
                                    status=status.HTTP_400_BAD_REQUEST)

            if not int(reset.date.day) <= int(reset.date.day) + 1:
                reset.delete()
                return JsonResponse({"result": False, "message": "This pin code is deprecated"},
                                    status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=reset.to_user.email)
            return JsonResponse({"result": True, "email": user.email, "message": "PIN is true"},
                                status=status.HTTP_200_OK)
        except:
            return JsonResponse({"result": False, "message": "PIN code not found"}, status=status.HTTP_404_NOT_FOUND)


class SetNewPasswordView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, email=None):
        try:
            reset = models.PasswordReset.objects.get(to_user=email, activate=False)
            serializer = SetNewPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            password = request.data.get("password")
            user = User.objects.get(email=email)
            user.set_password(password)
            reset.activate = True
            reset.save()
            auth.info("user {}, email {} reset password".format(user, email))
            return JsonResponse({"result": True, "message": "Password reset success"},
                                status=status.HTTP_200_OK)
        except:
            return JsonResponse({"result": False, "message": "Password not reset"})


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
        return username

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
        auth.info("google auth to user {}".format(user))
        return response


class LoginEmail(APIView):
    permission_classes = [AllowAny]

    def auth(self, email):
        backend = PasswordlessAuthBackend()
        user = backend.authenticate(email=email)
        try:
            user.auth_token.delete()
        except Exception as e:
            pass
        Token.objects.create(user=user)
        return user

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        user = self.auth(email)
        response = JsonResponse({"result": True, "token": user.auth_token.key})
        response.set_cookie('token', user.auth_token.key, httponly=True)
        return response


class FigmaView(APIView):

    def post(self, request):
        external_api_url = "https://www.figma.com/api/oauth/token?" \
                           f"client_id={getattr(settings, 'FIGMA_CLIENT')}&" \
                           f"client_secret={getattr(settings, 'FIGMA_SECRET')}&" \
                           f"redirect_uri={getattr(settings, 'FIGMA_REDIRECT_URI')}&" \
                           f"code={request.data.get('code')}&" \
                           "grant_type=authorization_code"
        data = request.POST
        res = requests.post(external_api_url, data)
        response_data = res.json()
        queryset = models.FigmaUser.objects.filter(user=request.user)
        try:
            figma_user = models.FigmaUser.objects.create(
                access_token=response_data['access_token'],
                refresh_token=response_data['refresh_token'],
                figma_user=response_data['user_id'],
                user=request.user
            )
            response = JsonResponse(response_data)
            queryset.delete()
            figma_user.save()
            figma.info("Add figma user {} to user {}".format(response_data['access_token'], request.user))
            response.set_cookie('access_token', response_data['access_token'], httponly=True)
        except:
            pass
        return JsonResponse(response_data)

    def get(self, request, *args, **kwargs):
        queryset = models.FigmaUser.objects.get(user=request.user)
        serializer = FigmaUserSerializer(queryset)
        return JsonResponse(serializer.data)

    def delete(self, request):
        try:
            queryset = models.FigmaUser.objects.get(user=request.user)
            queryset.delete()
            return JsonResponse({"result": True, "message": "User has been deleted"})
        except:
            return JsonResponse({"result": False, "message": "User has not been deleted"})


class FigmaUserRefresh(APIView):
    def post(self, request):
        external_api_url = "https://www.figma.com/api/oauth/refresh?" \
                           f"client_id={getattr(settings, 'FIGMA_CLIENT')}&" \
                           f"client_secret={getattr(settings, 'FIGMA_SECRET')}&" \
                           f"refresh_token={request.data.get('refresh_token')}"
        data = request.POST
        res = requests.post(external_api_url, data)
        response_data = res.json()
        queryset = models.FigmaUser.objects.get(user=request.user)
        queryset.access_token = response_data['access_token']
        queryset.save()
        response = JsonResponse(response_data)
        response.set_cookie('access_token', response_data['access_token'], httponly=True)
        return response


class LocalFigmaView(APIView):

    def post(self, request):
        external_api_url = "https://www.figma.com/api/oauth/token?" \
                           f"client_id={getattr(settings, 'FIGMA_CLIENT')}&" \
                           f"client_secret={getattr(settings, 'FIGMA_SECRET')}&" \
                           f"redirect_uri={'http://localhost:3000/0auth/callback'}&" \
                           f"code={request.data.get('code')}&" \
                           "grant_type=authorization_code"
        data = request.POST
        res = requests.post(external_api_url, data)
        response_data = res.json()
        queryset = models.FigmaUser.objects.filter(user=request.user)
        try:
            figma_user = models.FigmaUser.objects.create(
                access_token=response_data['access_token'],
                refresh_token=response_data['refresh_token'],
                figma_user=response_data['user_id'],
                user=request.user
            )
            response = JsonResponse(response_data)
            queryset.delete()
            figma_user.save()
            response.set_cookie('access_token', response_data['access_token'], httponly=True)
        except:
            pass
        return JsonResponse(response_data)

    def get(self, request, *args, **kwargs):
        queryset = models.FigmaUser.objects.get(user=request.user)
        serializer = FigmaUserSerializer(queryset)
        return JsonResponse(serializer.data)

    def delete(self, request):
        try:
            queryset = models.FigmaUser.objects.get(user=request.user)
            queryset.delete()
            return JsonResponse({"result": True, "message": "User has been deleted"})
        except:
            return JsonResponse({"result": False, "message": "User has not been deleted"})


class FigmaUserProfile(APIView):
    def get(self, request):
        external_api_url = 'https://api.figma.com/v1/me'
        data = request.POST
        figma_token = request.COOKIES.get('access_token')
        res = requests.get(external_api_url, data=data, headers={'X-FIGMA-TOKEN': figma_token})
        figma.info("User {} get profile {}".format(request.user, str(request.body)))
        return JsonResponse(res.json())
