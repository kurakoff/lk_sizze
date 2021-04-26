from rest_framework.authtoken.models import Token
from django.shortcuts import redirect


def open_access_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Methods"] = 'GET, POST, DELETE, PUT'
        return response
    return middleware


def check_token_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        try:
            token = request.META.get("HTTP_AUTHORIZATION")
            token = token.split()
            back_token = Token.objects.get(user=request.user)
            print(back_token)
            print(token)
            if token == back_token:
                pass
            else:
                return redirect("https://dashboard.sizze.io/sign-in")
        except:
            pass
        return response
    return middleware