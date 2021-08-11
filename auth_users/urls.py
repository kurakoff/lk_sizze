from django.urls import path, include
from . import views
from . import api

urlpatterns = [
    # path('', include('social_django.urls', namespace='social')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    path('users', api.UserCreate.as_view()),
    path('login', api.ApiLoginView.as_view()),
    path('logout', api.Logout.as_view()),
    path('login/google/', api.GoogleSocialAuthView.as_view()),
    path('login/email/', api.LoginEmail.as_view()),

    path('users/change/', api.UserUpdate.as_view()),
    path('users/profile', api.UserProfile.as_view()),
    path('password-reset/', api.ResetPasswordEmailView.as_view()),
    path('password-reset/pin/', api.SetPinView.as_view()),
    path('password-reset-complete/<email>/', api.SetNewPasswordView.as_view()),
    path('change-password/', api.ChangePassword.as_view()),

    path('create_account/', views.CreateAccount.as_view(), name='create_account'),
    # Reset password
    path('forgot_password/', views.CustomPasswordResetView.as_view(), name='forgot_password'),
    path('password_mail_done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_confirm_mail/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset'),
    path('reset_done/', views.SuccessResetPassword.as_view(), name='password_reset_complete'),

    path('figma/auth/', api.FigmaView.as_view()),
    path('local/figma/auth/', api.LocalFigmaView.as_view()),
    path('figma/auth/refresh/', api.FigmaUserRefresh.as_view()),
    # path('figma/user/', api.FigmaUserProfile.as_view()),

    path('user/about/', api.UserAboutView.as_view()),
    path('token/', api.TokenCheckApi.as_view()),

    path('enterprise/', api.EnterpriseApi.as_view()),
    path('enterprise/<int:user_id>/', api.EnterpriseDetailApi.as_view()),
    path('enterprise/<int:user_id>/task/', api.TasksApi.as_view()),
    path('enterprise/<int:user_id>/task/<int:task_id>/', api.TaskDetailApi.as_view()),

    path('generate_key_write/', api.GetRandomKeyWrite.as_view()),
    path('write/', api.PostWrite.as_view()),
    path('write/<str:key>/', api.PostWrite.as_view()),
]
#
#
# >>> from content import models
# >>> from django.contrib.auth.models import User
# >>> import os, base64
# >>> users = User.objects.all()
# >>> for user in users:
# ...     uniq = False
    # ...     while uniq is False:
# ...             promo = os.urandom(5)
# ...             promo = base64.b64encode(promo)
# ...             check_uniq = models.Pr
# models.Price(      models.Project(    models.Promocode(  models.Prototype(
# ...             check_uniq = models.Promocode.objects.filter(promo=promo)
