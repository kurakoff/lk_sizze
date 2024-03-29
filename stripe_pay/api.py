from datetime import date, datetime
import stripe
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from decouple import config
from content.models import ClientStrip, Price, Subscription, UserPermission, EnterpriseUser
from django.contrib.auth.models import User
from .serializers import *
from django.template.loader import render_to_string
from auth_users.utils import send_html_mail
from django.conf import settings
from sizzy_lk import settings
import requests
import json, amplitude

live_mode_turn = True
amplitude_logger = amplitude.AmplitudeLogger(api_key="bb7646a778c6c18c17fd261a7468ceca")
stripe.api_key = config("stripe_secret")


class Amplitude:
    def post(self, user, event):
        data={
          "api_key": config('amplitude_secret'),
          "events": [
            {
              "user_id": user['id'],
              "device_id": None,
              "event_type": event,
              "event_properties": {
              },
              "user_properties": {
                "isStaff": user['is_staff'],
                "email": user['email']
              }
            }
          ]
        }
        response = requests.post('https://api2.amplitude.com/2/httpapi', data=json.dumps(data)
        )
        return response


class StripeApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return_url = 'https://dashboard.sizze.io/'
        data = json.loads(request.body)
        try:
            customer = ClientStrip.objects.get(user=request.user, livemode=live_mode_turn)
        except Exception as e: customer = None
        if customer:
            sub = stripe.Subscription.list(customer=customer.client)
            for i in sub['data']:
                if i['plan']['id'] == data['priceId'] and i['status'] != 'incomplete':
                    return JsonResponse({'result': False, 'message': 'Sub is exist'}, status=status.HTTP_400_BAD_REQUEST)
            checkout_session = stripe.checkout.Session.create(
                success_url=return_url,
                cancel_url=return_url,
                customer=customer.client,
                payment_method_types=['card'],
                mode='subscription',
                allow_promotion_codes=True,
                locale='en',
                line_items=[{
                    'price': data['priceId'],
                    'quantity': 1
                }]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        else:
            try:
                checkout_session = stripe.checkout.Session.create(
                    success_url=return_url,
                    cancel_url=return_url,
                    payment_method_types=['card'],
                    mode='subscription',
                    allow_promotion_codes=True,
                    locale='en',
                    customer_email=request.user.email,
                    line_items=[{
                        'price': data['priceId'],
                        'quantity': 1
                    }]
                )
                return JsonResponse({'sessionId': checkout_session['id']})
            except Exception as e:
                return JsonResponse({'error': {'message': str(e)}}, status=status.HTTP_400_BAD_REQUEST)


class CheckoutPromocode(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return_url = 'https://dashboard.sizze.io/'
        data = json.loads(request.body)
        try:
            customer = ClientStrip.objects.get(user=request.user, livemode=live_mode_turn)
        except Exception as e: customer = None
        if customer and customer.user.promocode.discount is True:
            sub = stripe.Subscription.list(customer=customer.client)
            for i in sub['data']:
                if i['plan']['id'] == data['priceId'] and i['status'] != 'incomplete':
                    return JsonResponse({'result': False, 'message': 'Sub is exist'}, status=status.HTTP_400_BAD_REQUEST)
            checkout_session = stripe.checkout.Session.create(
                success_url=return_url,
                cancel_url=return_url,
                customer=customer.client,
                payment_method_types=['card'],
                mode='subscription',
                locale='en',
                discounts=[{"coupon": "Sc7tw02X"}],
                line_items=[{
                    'price': data['priceId'],
                    'quantity': 1
                }]
            )
            promo = customer.user.promocode
            promo.discount = True
            promo.save()
            return JsonResponse({'sessionId': checkout_session['id']})
        else:
            try:
                checkout_session = stripe.checkout.Session.create(
                    success_url=return_url,
                    cancel_url=return_url,
                    payment_method_types=['card'],
                    mode='subscription',
                    discounts=[{"coupon": "Sc7tw02X"}],
                    locale='en',
                    customer_email=request.user.email,
                    line_items=[{
                        'price': data['priceId'],
                        'quantity': 1
                    }]
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
            signature = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, sig_header=signature, secret=webhook_secret)
                data = event['data']
            except Exception as e:
                return e
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']
        data_object = data['object']
        if event_type == 'checkout.session.completed':
            return JsonResponse({"result": True})
        elif event_type == 'invoice.paid':
            user = User.objects.get(email=data_object['customer_email'])
            try:
                from auth_users.utils import send_text_mail
                send_text_mail(f"{user.email} купил подпику, проверьте страйп",
                               f"{user.email} купил подпику, проверьте страйп",
                               sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>',
                               recipient_list=['kabiljanz0301@gmail.com', 'kurakoff19@gmail.com'])
            except:
                pass
            product = Price.objects.get(price=data_object['lines']['data'][0]['price']['id'])
            if product.name == "Enterprise":
                event_args = {"user_id": str(user.id), "event_type": "Subscription (Enterprise)"}
                event = amplitude_logger.create_event(**event_args)
                amplitude_logger.log_event(event)
                perm = user.userpermission
                perm.permission = 'ENTERPRISE'
                perm.save()
                try:
                    EnterpriseUser.objects.get(user=user)
                except:
                    enterprise = EnterpriseUser.objects.create(
                        user=user,
                        telegram=None
                    )
                    enterprise.save()
                msg_html = render_to_string('content/plan_enterprise.html')
                send_html_mail(subject="Welcome to sizze.io", html_content=msg_html,
                               sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>',
                               recipient_list=[user.email])
            if product.name == "Team":
                event_args = {"user_id": str(user.id), "event_type": "Subscription (Team)"}
                event = amplitude_logger.create_event(**event_args)
                amplitude_logger.log_event(event)
                perm = user.userpermission
                perm.permission = 'TEAM'
                perm.save()
                msg_html = render_to_string('content/plan_team.html')
                send_html_mail(subject="Welcome to sizze.io", html_content=msg_html,
                               sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>',
                               recipient_list=[user.email])
            if product.name == "Professional":
                event_args = {"user_id": str(user.id), "event_type": "Subscription (Professional)"}
                event = amplitude_logger.create_event(**event_args)
                amplitude_logger.log_event(event)
                perm = user.userpermission
                perm.permission = 'PROFESSIONAL'
                perm.save()
                msg_html = render_to_string('content/Plan.html',)
                send_html_mail(subject="Welcome to sizze.io", html_content=msg_html,
                               sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>',
                               recipient_list=[user.email])
        elif event_type == 'invoice.payment_failed':
            user = User.objects.get(email=data_object['customer_email'])
            event_args = {"user_id": str(user.id), "event_type": "Subscription (Start)"}
            event = amplitude_logger.create_event(**event_args)
            amplitude_logger.log_event(event)
            perm = user.userpermission
            perm.permission = 'START'
            perm.save()
            msg_html = render_to_string('content/plan_free.html')
            send_html_mail(subject="Welcome to sizze.io", html_content=msg_html,
                           sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>',
                           recipient_list=[user.email])
            user.save()
        elif event_type == 'customer.subscription.deleted':
            # try:
            sub = Subscription.objects.get(subscription=data_object['id'])
            customer = sub.customer.user
            permission = UserPermission.objects.get(user=customer)
            permission.permission = 'START'
            permission.save()
            sub.delete()
            event_amplitude = Amplitude()
            event_amplitude.post(user=customer, event='Subscription (Start)')
            # except Exception as e:
            #     print(e)
        elif event_type == 'customer.subscription.created':

            stripe.api_key = config('stripe_secret')
            client = ClientStrip.objects.get(client=data_object['customer'])
            # client.use_trial = True
            plan = Price.objects.get(price=data_object['plan']['id'])
            try:
                past_sub = Subscription.objects.get(customer=client)
                past_plan_name = past_sub.plan.name
                plan_name = plan.name
                if past_plan_name == 'Professional' and plan_name == 'Team':
                    stripe.Subscription.delete(past_sub.subscription)
            except: pass
            Subscription.objects.create(
                subscription=data_object['id'],
                plan=plan,
                end_period=data_object['current_period_end'],
                start_period=data_object['current_period_start'],
                customer=client,
                latest_invoice=data_object["latest_invoice"],
                status=data_object['status'],
                subscription_end=data_object['ended_at'],
                livemode=data_object['livemode']
            )
            client.save()

        elif event_type == 'customer.subscription.updated':
            try:
                sub = Subscription.objects.get(
                    subscription=data_object['id'],
                )
                sub.end_period = data_object['current_period_end']
                sub.start_period = data_object['current_period_start']
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
        return_url = 'https://dashboard.sizze.io/'
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
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, sig_header=signature, secret=webhook_secret)
                data = event['data']
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
        elif event_type == 'customer.created':
            client = data['object']['id']
            email = data['object']['email']
            user = User.objects.get(email=email)
            new_client = ClientStrip.objects.create(
                user=user, client=client, seanse=data_object['id'], livemode=data_object["livemode"], use_trial=False)
            new_client.save()
            return JsonResponse({'result': True})
        elif event_type == 'customer.updated':
            try:
                client = ClientStrip.objects.get(user=request.user)
                client.payment_status = data_object['payment_status']
                return JsonResponse({'result': True})
            except Exception:
                return JsonResponse({'result': False})
        elif event_type == 'customer.deleted':
            client = ClientStrip.objects.get(client=data_object['id'])
            permission = UserPermission.objects.get(user=client.user)
            permission.permission = 'START'
            permission.save()
            client.delete()
            return JsonResponse({'result': True})


class GetPrice(APIView):
    def get(self, request):
        price = Price.objects.filter(live_mode=live_mode_turn)
        serializer = PriceSerializer(price, many=True)
        subs = []
        try:
            customer = ClientStrip.objects.get(user=request.user, live_mode=live_mode_turn)
            sub = stripe.Subscription.list(customer=customer.client)
            for i in sub['data']:
                subs.append(i['plan']['id'])
        except: pass
        for i in serializer.data:
            if i['price'] in subs:
                i['user_status'] = True
            else:
                i['user_status'] = False
        return Response(serializer.data)

