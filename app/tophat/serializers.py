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
from rest_framework.exceptions import ValidationError
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

    def validate_name(self, value):
        if Categories.objects.filter(name=value).exists():
            raise ValidationError("A category with this name already exists.")
        return value

    def create(self, validated_data):
        return Categories.objects.create(**validated_data)


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
        fields = ['amount', 'order_status', 'payment_status', 'items', 'order_date', 'order_time']


class OrderItemsSerializer(serializers.Serializer):
    """Serializer for Order Items Object"""

    user = 'user.serializers.UserSerializer'

    user_id = serializers.IntegerField(required=False)
    order_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    size_id = serializers.IntegerField(required=False)
    extras = serializers.ListField()
    kitchen_notes = serializers.ListField()
    quantity = serializers.IntegerField(required=False)
    total = serializers.IntegerField(required=False)

    def create(self, validated_data):
        """Create and return a Order Items instance"""
        order_id = validated_data.pop('order_id', None)
        item_id = validated_data.pop('item_id', None)
        size_id = validated_data.pop('size_id', None)
        quantity = validated_data.pop('quantity', None)
        extras = validated_data.pop('extras', [])
        kitchen_notes = validated_data.pop('kitchen_notes', [])
        total = validated_data.pop('total', None)

        extras = ",".join(extras)
        kitchen_notes = ",".join(kitchen_notes)

        orderItems = OrderItems.objects.create(
            order=order_id,
            item=item_id,
            size=size_id,
            extras=extras,
            kitchen_notes=kitchen_notes,
            quantity=quantity,
            total=total,
            **validated_data
        )

        return orderItems

    def to_representation(self, instance):
        """Include orderItems_id in the serialized representation"""
        representation = super().to_representation(instance)
        representation['order_id'] = instance.id
        representation['extras'] = instance.platform.split(",")
        representation['kitchen_notes'] = instance.keywords.split(",")

        return representation


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = [
            'id', 'menu_item', 'name', 'price'
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
    extras = serializers.ListField(required=False, allow_empty=True)
    kitchen_notes = serializers.ListField(required=False, allow_empty=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'item', 'quantity', 'total', 'extras', 'kitchen_notes', 'size']
        read_only_fields = ['id', 'user']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def get_item_name(self, obj):
        cart_items = self.context.get('cart_items', [])
        item = next((item for item in cart_items if item.id == obj.id), None)
        return item.item.name if item else ''

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     # Convert extras and kitchen_notes strings to lists of integers
    #     extras = instance.extras
    #     if extras:
    #         try:
    #             data['extras'] = [int(item) for item in extras.strip('[]').split(',')]
    #         except ValueError:
    #             data['extras'] = []

    #     kitchen_notes = instance.kitchen_notes
    #     if kitchen_notes:
    #         try:
    #             data['kitchen_notes'] = [int(item) for item in kitchen_notes.strip('[]').split(',')]
    #         except ValueError:
    #             data['kitchen_notes'] = []

    #     return data




class CartItemCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=False)
    size =  serializers.CharField(required=False)
    total = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
    extras = serializers.ListField(required=False, allow_empty=True)
    kitchen_notes = serializers.ListField(required=False, allow_empty=True)

    def validate(self, data):
        item_id = data.get('item_id')
        quantity = data.get('quantity')

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")

        return data