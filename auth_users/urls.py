from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import path
from .views import \
    LoginView, \
    CreateAccount, \
    SuccessResetPassword, \
    CustomPasswordResetDoneView, \
    CustomPasswordResetConfirmView, CustomPasswordResetView

# AUTH URLS


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('create_account/', CreateAccount.as_view(), name='create_account'),

    path('forgot_password/', CustomPasswordResetView.as_view(), name='forgot_password'),
    path('password_mail_done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_confirm_mail/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset'),
    path('reset_done/', SuccessResetPassword.as_view(), name='password_reset_complete'),
]
