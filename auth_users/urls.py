from django.urls import path, include
from . import views
from . import api


urlpatterns = [
    # path('', include('social_django.urls', namespace='social')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('users', api.UserCreate.as_view()),
    path('login', api.ApiLoginView.as_view()),
    path('login/google/', api.GoogleSocialAuthView.as_view()),

    path('users/change', api.UserUpdate.as_view()),
    path('users/profile', api.UserProfile.as_view()),
    path('password-reset/', api.RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         api.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', api.SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
    path('change_password', api.ChangePassword.as_view()),

    path('create_account/', views.CreateAccount.as_view(), name='create_account'),
    # Reset password
    path('forgot_password/', views.CustomPasswordResetView.as_view(), name='forgot_password'),
    path('password_mail_done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_confirm_mail/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset'),
    path('reset_done/', views.SuccessResetPassword.as_view(), name='password_reset_complete'),
]