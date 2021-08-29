from . import api
from django.urls import path


urlpatterns = [
    path('create-checkout-session/', api.StripeApi.as_view()),
    path('create-checkout-session/promo-discount/', api.CheckoutPromocode.as_view()),
    path('webhook/', api.StripeWebhook.as_view()),
    path('customer-portal/', api.ClientPortal.as_view()),
    path('price/', api.PriceWebhook.as_view()),
    path('price_list/', api.GetPrice.as_view())
]