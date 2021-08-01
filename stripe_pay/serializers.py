from rest_framework import serializers
from content.models import ClientStrip, Price, Subscription

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class ClientStripeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStrip
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'