from django.urls import path, include

from .views import LoginView, ForgotPassword

# AUTH URLS

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('forgot_password/', ForgotPassword.as_view(), name='forgot_password'),
]
