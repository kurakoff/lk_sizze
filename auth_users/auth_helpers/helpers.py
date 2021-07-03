from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import TokenAuthentication

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


class TokenAuthSupportCookie(TokenAuthentication):
    def authenticate(self, request):
        if 'access_token' in request.COOKIES:
            return self.authenticate_credentials(
                request.COOKIES.get('access_token')
            )
        return super().authenticate(request)