from rest_framework import serializers
from core.models import(
    Categories,
    Feedback,
    MenuItems,
    # Payments,
    Orders,
    OrderItems,
    LoyaltyPoints,
    # Cart
)
from rest_framework.response import Response
from rest_framework import (
    status,
)
from decimal import Decimal


class CategoriesSerializer(serializers.ModelSerializer):
    """Serializer for Categories Object"""
    class Meta:
        model = Categories
        fields = [
            'id', 'name', 'creation_date', 'created_by',
            'last_update_date', 'last_updated_by', 'last_update_login'
            ]

        read_only_fields = [
            'id', 'creation_date', 'created_by',
            'price', 'last_updated_by', 'last_update_login'
            ]


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback Object"""
    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'message', 'creation_date', 'created_by',
            'last_update_date', 'last_updated_by', 'last_update_login'
        ]

        read_only_fields = [
            'id', 'user', 'creation_date', 'created_by',
            'price', 'last_updated_by', 'last_update_login'
            ]


class MenuItemsSerializer(serializers.ModelSerializer):
    """Serializer for MenuItems Object"""
    class Meta:
        model = MenuItems
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'image', 'image1', 'image2', 'image3', 'image4', 'image5'
        ]

        read_only_fields = [
            'id'
        ]


class LoyaltyPointsSerializer(serializers.Serializer):
    """Serializer for LoyaltyPoints Object"""

    user = 'user.serializers.UserSerializer'

    points = serializers.DecimalField(required=True, max_digits=20, decimal_places=3)

    def create(self, validated_data):
        """Add points based on order value"""

        user_id = self.context['request'].user
        order_value = validated_data.pop('points', None)

        points_earned = Decimal(order_value) * Decimal('0.1')

        loyalty_points_instance, created = LoyaltyPoints.objects.get_or_create(user=user_id)

        if created:
            loyalty_points_instance.points = points_earned
        else:
            loyalty_points_instance.points += points_earned

        loyalty_points_instance.save()

        return loyalty_points_instance


class OrderItemSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=MenuItems.objects.all())

    class Meta:
        model = OrderItems
        fields = ['item', 'quanity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Orders
        fields = ['amount', 'order_status', 'payment_status', 'items']