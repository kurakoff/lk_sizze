from . import api
from django.urls import path


urlpatterns = [
    path('create-checkout-session/', api.StripeApi.as_view()),
]