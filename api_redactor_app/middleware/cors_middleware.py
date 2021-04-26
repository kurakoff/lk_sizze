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
            Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            print('check token')
            return redirect("https://dashboard.sizze.io/sign-in")
        except:
            pass
        return response
    return middleware