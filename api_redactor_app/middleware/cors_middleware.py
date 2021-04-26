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
            token_list = []
            token = token.split()
            back_token = Token.objects.all().values('key')
            for i in back_token['key']:
                token_list.append(i)
            if token[1] not in token_list:
                print('Tam')
                return redirect("https://dashboard.sizze.io/sign-in")
        except Token.DoesNotExist:
            print('check token')
            return redirect("https://dashboard.sizze.io/sign-in")
        except:
            pass
        return response
    return middleware
