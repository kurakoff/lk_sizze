from . import api
from django.urls import path


urlpatterns = [
    path('create-checkout-session/', api.StripeApi.as_view()),
    path('webhook/', api.StripeWebhook.as_view()),
    path('customer-portal/', api.ClientPortal.as_view())
]