from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import IndexView, ProfileView, ProfileSaveDetailsView

# CONTENT URLS
urlpatterns = [
    path('', login_required(IndexView.as_view()), name='index'),
    path('profile/', login_required(ProfileView.as_view()), name='user_profile'),
    path('profile/save_details', login_required(ProfileSaveDetailsView.as_view()), name='user_save_details'),
]
