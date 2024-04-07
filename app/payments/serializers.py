from rest_framework import serializers
from core.models import Payments


class PaymentSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField(max_length=500, required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    order_date = serializers.DateField()
    order_time = serializers.TimeField()


class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'
        read_only_fields = [
            'user'
            ]
