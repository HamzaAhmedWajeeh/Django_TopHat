from rest_framework import serializers
from core.models import(
    Categories,
    Feedback,
    MenuItems,
    # Payments,
    Orders,
    OrderItems,
    LoyaltyPoints,
    Cart,
    ItemExtras,
    Extras,
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
        fields = ['item', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Orders
        fields = ['amount', 'order_status', 'payment_status', 'items']


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = [
            'id', 'items', 'name', 'price'
            ]
        read_only_fields = [
            'creation_date', 'created_by', 'last_updated_by',
            'last_update_login', 'last_update_date', 'id'
            ]


class ItemExtrasSerializer(serializers.ModelSerializer):
    extras = ExtrasSerializer()

    class Meta:
        model = ItemExtras
        fields = [
            'id', 'extras', 'creation_date', 'created_by',
            'last_update_date', 'last_updated_by', 'last_update_login'
            ]
        read_only_fields = [
            'id', 'creation_date', 'created_by', 'last_updated_by',
            'last_update_login', 'last_update_date'
            ]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'item', 'quanity', 'total']

        read_only_fields = ['id', 'user']

        def validate_quantity(self, value):
            if value <= 0:
                raise serializers.ValidationError("Quantity must be a positive integer.")
            return value

        def get_item_name(self, obj):
            cart_items = self.context.get('cart_items', [])
            item = next((item for item in cart_items if item.id == obj.id), None)
            return item.item.name if item else ''


class CartItemCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate(self, data):
        item_id = data.get('item_id')
        quantity = data.get('quantity')

        # You can add custom validation logic here

        return data