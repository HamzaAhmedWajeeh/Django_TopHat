from rest_framework import serializers
from tophat.serializers import OrderItemSerializer


class PaymentSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField(max_length=500, required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    # items = OrderItemSerializer(many=True)
    order_date = serializers.DateField()
    order_time = serializers.TimeField()


class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
