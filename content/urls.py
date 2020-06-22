from django.urls import path

from auth_users.views import ForgotPassword
from .views import IndexView

# CONTENT URLS
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]
