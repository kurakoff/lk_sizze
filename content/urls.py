from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import IndexView, ProfileView, ProfileSaveDetailsView, CreateProjectView, DeleteProject, CopyProject

# CONTENT URLS
urlpatterns = [
    path('', login_required(IndexView.as_view()), name='index'),
    path('create_project/', login_required(CreateProjectView.as_view()), name='create_project'),
    path('delete_project/', login_required(DeleteProject.as_view()), name='delete_project'),
    path('copy_project/', login_required(CopyProject.as_view()), name='copy_project'),

    path('profile/change_password', login_required(ProfileView.as_view()), name='change_password'),
    path('profile/save_details', login_required(ProfileSaveDetailsView.as_view()), name='user_save_details'),
]
