"""sizzy_lk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from auth_users.auth_helpers.sso import Server


class ServerForMisago(Server):
    def get_user_data(self, user, *args, **kwargs) -> dict:
        user_data = super().get_user_data(user, *args, **kwargs)
        user_data['id'] = user.pk
        print(user_data)
        return user_data

    def get_user_extra_data(self, user, consumer, extra_data) -> dict:
        return {}


sso_server = ServerForMisago()

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('content.urls')),
                  path('user/', include('auth_users.urls')),
                  path('api/editor/', include('api_redactor_app.urls')),
                  path('api/auth/', include('auth_users.urls')),
                  path('nested_admin/', include('nested_admin.urls')),
                  path('tinymce/', include('tinymce.urls')),
                  path('pay/', include('stripe_pay.urls'))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('server/', include(sso_server.get_urls()))
]