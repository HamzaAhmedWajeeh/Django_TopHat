from rest_framework import serializers
from tophat.serializers import OrderItemSerializer


class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method_id = serializers.CharField(max_length=255, required=True)
    items = OrderItemSerializer(many=True)
    order_date = serializers.DateField()
    order_time = serializers.TimeField()
