from django.urls import path, include

from .views import LoginView, ForgotPassword, CreateAccount, SuccessResetMailSend, SelectPassword, SuccessResetPassword

# AUTH URLS

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('forgot_password/', ForgotPassword.as_view(), name='forgot_password'),
    path('create_account/', CreateAccount.as_view(), name='create_account'),
    path('success_reset_mail/', SuccessResetMailSend.as_view(), name='success_reset_mail_send'),
    path('select_password/', SelectPassword.as_view(), name='success_reset_mail_send'),
    path('success_reset_password/', SuccessResetPassword.as_view(), name='success_reset_password'),
]
