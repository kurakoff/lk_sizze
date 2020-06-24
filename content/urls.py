from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import IndexView

# CONTENT URLS
urlpatterns = [
    path('', login_required(IndexView.as_view()), name='index'),
]
