import json
import os
import stripe
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from decouple import config

stripe.api_key = config('stripe_secret')


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


class StripeWebhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        webhook_secret = config('stripe_webhook')
        request_data = json.loads(request.body)
        if webhook_secret:
            # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
            signature = request.headers.get('stripe-signature')
            print(signature)
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, sig_header=signature, secret=webhook_secret)
                data = event['data']
                print("try")
            except Exception as e:
                print(e)
                return e
            # Get the type of webhook event sent - used to check the status of PaymentIntents.
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']
        data_object = data['object']
        print(event_type)
        if event_type == 'checkout.session.completed':
            print(data)
        elif event_type == 'invoice.paid':
            # Continue to provision the subscription as payments continue to be made.
            # Store the status in your database and check when a user accesses your service.
            # This approach helps you avoid hitting rate limits.
            print(data)
        elif event_type == 'invoice.payment_failed':
            # The payment failed or the customer does not have a valid payment method.
            # The subscription becomes past_due. Notify your customer and send them to the
            # customer portal to update their payment information.
            print(data)
        else:
            print('Unhandled event type {}'.format(event_type))
        return JsonResponse({'status': 'success'})


class ClientPortal(APIView):
    def post(self, request):
        return_url = 'https://dashboard.sizze.io/'
        session = stripe.billing_portal.Session.create(
            customer='{{CUSTOMER_ID}}',
            return_url=return_url)
        return JsonResponse({'url': session.url})

