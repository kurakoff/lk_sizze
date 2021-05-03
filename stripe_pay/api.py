import json
import os
import stripe
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

stripe.api_key = "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"


class StripeApi(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        data = json.loads(request.body)
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url='https://dashboard.sizze.io/',
                            #'?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://dashboard.sizze.io/',
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{
                    'price': data['priceId'],
                    # For metered billing, do not pass quantity
                    'quantity': 1
                }],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': {'message': str(e)}}, status=status.HTTP_400_BAD_REQUEST)
