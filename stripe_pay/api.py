import json
import stripe
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from decouple import config
from content.models import ClientStrip, Price, Subscription, UserPermission
from django.contrib.auth.models import User
from .serializers import *

stripe.api_key = config('stripe_secret')


class StripeApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = json.loads(request.body)
        try:
            customer = ClientStrip.objects.get(user=request.user)
        except Exception as e: customer = None
        if customer:
            sub = stripe.Subscription.list(customer=customer.client)
            for i in sub['data']:
                print(i)
                if i['plan']['id'] == data['priceId']:
                    return JsonResponse({'result': False, 'message': 'Sub is exist'}, status=status.HTTP_400_BAD_REQUEST)
            checkout_session = stripe.checkout.Session.create(
                success_url='http://localhost:3000/',
                            #'?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:3000/',
                customer=customer.client,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{
                    'price': data['priceId'],
                    'quantity': 1
                }],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        else:
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
            try:
                client = data['object']['customer']
                email = data['object']['customer_details']['email']
                user = User.objects.get(email=email)
                past_client = ClientStrip.objects.filter(user=user)
                past_client.delete()
                ClientStrip.objects.create(user=user, client=client, payment_status=data_object['payment_status'],
                                           seanse=data_object['id'], livemode=data_object["livemode"])
                return JsonResponse({"result": True})
            except Exception:
                return JsonResponse({"result": False})
        elif event_type == 'invoice.paid':
            permission = UserPermission.objects.get(user_email=data_object['customer_email'])
            product = Price.objects.get(price=data_object['lines']['data']['price']['id'])
            if product.name == "Team":
                permission.start = False
                permission.team = True
                permission.professional = False
            if product.name == "Professional":
                permission.start = False
                permission.professional = True
                permission.team = False
        elif event_type == 'invoice.payment_failed':
            permission = UserPermission.objects.get(user=request.user)
            permission.start = True
            permission.team = False
            permission.professional = False
        elif event_type == 'customer.subscription.deleted':
            try:
                sub = Subscription.objects.get(subscription=data_object['id'])
                sub.delete()
            except Exception as e:
                print(e)
            permission = UserPermission.objects.get(user=request.user)
            permission.start = True
            permission.professional = False
            permission.team = False
        elif event_type == 'customer.subscription.created':
            # try:
            Subscription.objects.create(
                subscription=data_object['id'],
                end_period=data_object['current_period_end'],
                start_period=data_object['current_period_start'],
                customer=data_object['customer'],
                latest_invoice=data_object["latest_invoice"],
                status=data_object['status'],
                subscription_end=data_object['ended_at'],
                livemode=data_object['livemode']
            )
            # except Exception as e:
            #     print(e)
        elif event_type == 'customer.subscription.updated':
            try:
                sub = Subscription.objects.get(
                    subscription=data_object['id'],
                )
                sub.end_period = data_object['current_period_end']
                sub.start_period = data_object['current_period_start']
                sub.customer = data_object['customer']
                sub.latest_invoice = data_object["latest_invoice"]
                sub.status = data_object['status']
                sub.subscription_end = data_object['ended_at']
                sub.save()
            except Exception as e:
                print(e)
        else:
            print('Unhandled event type {}'.format(event_type))
        return JsonResponse({'status': 'success'})


class ClientPortal(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return_url = 'http://localhost:3000/'
        try:
            customer = ClientStrip.objects.get(user=request.user)
            session = stripe.billing_portal.Session.create(
                customer=customer.client,
                return_url=return_url)
            return JsonResponse({'url': session.url})
        except:
            return JsonResponse({'result': False})


class SubscriptionStripe(APIView):
    pass


class PriceWebhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        webhook_secret = config('stripe_webhook_price')
        request_data = json.loads(request.body)
        if webhook_secret:
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
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']
        data_object = data['object']
        if event_type == 'price.created':
            try:
                product = stripe.Product.retrieve(id=data_object['product'])
                Price.objects.create(
                    price=data_object['id'],
                    product=data_object['product'],
                    status=data_object['active'],
                    live_mode=data_object['livemode'],
                    cost=data_object['unit_amount'],
                    name=product['name'],
                    interval=data_object['recurring']['interval']
                )
                return JsonResponse({'result': True})
            except Exception:
                return JsonResponse({'result': False})

        elif event_type == 'price.updated':
            try:
                price = Price.objects.get(price=data_object['id'])
                price.status = data_object['active']
                price.live_mode = data_object['livemode']
                price.cost = data_object['unit_amount']
                price.save()
                return JsonResponse({'result': True})
            except Exception:
                return JsonResponse({'result': False})

        elif event_type == 'price.deleted':
            try:
                price = Price.objects.get(price=data_object['id'])
                price.delete()
                return JsonResponse({'result': True})
            except Exception:
                return JsonResponse({'result': False})
        elif event_type == 'customer.updated':
            try:
                client = ClientStrip.objects.get(user=request.user)
                client.payment_status = data_object['payment_status']
                return JsonResponse({'result': True})
            except Exception:
                return JsonResponse({'result': False})
        elif event_type == 'customer.deleted':
            try:
                client = ClientStrip.objects.get(client=data_object['id'])
                client.delete()
                return JsonResponse({'result': True})
            except Exception:
                return JsonResponse({'result': False})


class GetPrice(APIView):
    def get(self, request):
        price = Price.objects.all()
        serializer = PriceSerializer(price, many=True)
        subs = []
        try:
            customer = ClientStrip.objects.get(user=request.user)
            sub = stripe.Subscription.list(customer=customer.client)
            for i in sub['data']:
                subs.append(i['plan']['id'])
        except: pass
        for i in serializer.data:
            print(i)
            if i['price'] in subs:
                i['user_status'] = True
            else:
                i['user_status'] = False
        return Response(serializer.data)
