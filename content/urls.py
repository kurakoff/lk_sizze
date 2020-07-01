from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import IndexView, ProfileView, ProfileSaveDetailsView, CreateProjectView, DeleteProjectView, \
    CopyProjectView, \
    EditProjectView, RedactorView, TestView, CreateScreenView

# CONTENT URLS
urlpatterns = [
    path('', login_required(IndexView.as_view()), name='index'),
    path('create_project/', login_required(CreateProjectView.as_view()), name='create_project'),
    path('delete_project/', login_required(DeleteProjectView.as_view()), name='delete_project'),
    path('copy_project/', login_required(CopyProjectView.as_view()), name='copy_project'),
    path('rename_project/', login_required(EditProjectView.as_view()), name='edit_project'),

    path('create_screen/', login_required(CreateScreenView.as_view()), name='create_screen'),
    # path('delete_screen/', login_required(DeleteScreenView.as_view()), name='delete_screen'),
    # path('copy_screen/', login_required(CopyScreenView.as_view()), name='copy_screen'),
    # path('rename_delete/', login_required(EditProjectView.as_view()), name='edit_screen'),

    path('redactor/<int:project>', login_required(RedactorView.as_view()), name='redactor'),

    path('profile/change_password', login_required(ProfileView.as_view()), name='change_password'),
    path('profile/save_details', login_required(ProfileSaveDetailsView.as_view()), name='user_save_details'),

    path('test/', login_required(TestView.as_view()), name='test'),

]
