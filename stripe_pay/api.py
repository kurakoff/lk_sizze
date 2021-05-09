import json
import stripe
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from decouple import config
from content.models import ClientStrip, Price
from django.contrib.auth.models import User

stripe.api_key = config('stripe_secret')


class StripeApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = json.loads(request.body)
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url='http://localhost:3000/',
                            #'?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:3000/',
                payment_method_types=['card'],
                mode='subscription',
                customer_email=request.user.email,
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
            print(data['object']['customer'])
            client = data['object']['customer']
            email = data['object']['customer_details']['email']
            user = User.objects.get(email=email)
            ClientStrip.objects.create(user=user, client=client)
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
        elif event_type == 'customer.subscription.deleted':
            print('deleted')
            print(data)
        elif event_type == 'customer.subscription.created':
            print('deleted')
            print(data)
        elif event_type == 'customer.subscription.updated':
            print('deleted')
            print(data)
        else:
            print('Unhandled event type {}'.format(event_type))
        return JsonResponse({'status': 'success'})


class ClientPortal(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return_url = 'http://localhost:3000/'
        customer = ClientStrip.objects.get(user=request.user)
        session = stripe.billing_portal.Session.create(
            customer=customer.client,
            return_url=return_url)
        return JsonResponse({'url': session.url})


class SubscriptionStripe(APIView):
    pass


class PriceWebhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        webhook_secret = config('stripe_webhook_price')
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
        if event_type == 'price.created':
            product = stripe.Product.retrieve(id=data['product'])
            Price.objects.create(
                price=data['id'],
                product=data['product'],
                status=data['active'],
                live_mode=data['livemode'],
                cost=data['unit_amount'],
                name=product['name']
            )
        elif event_type == 'price.updated':
            price = Price.objects.get(price=data['id'])
            price.status = data['active']
            price.live_mode = data['livemode']
            price.cost = data['unit_amount']
            price.save()
        elif event_type == 'price.deleted':
            price = Price.objects.get(price=data['id'])
            price.delete()


class GetPrice(APIView):
    def get(self, request):
        price = stripe.Price.list(api_key=stripe.api_key)
        print(price)
        return Response({'result': "ok"})