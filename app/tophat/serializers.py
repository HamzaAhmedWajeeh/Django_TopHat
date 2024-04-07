from rest_framework import serializers
from core.models import(
    Categories,
    Feedback,
    MenuItems,
    LoyaltyPointsPercentage,
    Orders,
    OrderItems,
    LoyaltyPoints,
    Cart,
    ItemExtras,
    Extras,
    Sizes,
    OrderNotifications,
    KitchenNotes
)
from rest_framework.exceptions import ValidationError
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

    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'user_email', 'user_name', 'message', 'creation_date', 'created_by',
            'last_update_date', 'last_updated_by', 'last_update_login'
        ]

        read_only_fields = [
            'id', 'user', 'creation_date', 'created_by',
            'price', 'last_updated_by', 'last_update_login', 'user_obj'
            ]

        def to_representation(self, instance):
            """Override to include user_name and user_email"""
            representation = super().to_representation(instance)
            representation.pop('user')  # Remove user field from response
            return representation


class MenuItemsSerializer(serializers.ModelSerializer):
    """Serializer for MenuItems Object"""
    class Meta:
        model = MenuItems
        fields = [
            'id', 'name', 'description', 'price', 'category', 'large_price', 'medium_price', 'small_price',
            'image', 'image1', 'image2', 'image3', 'image4', 'image5', 'created_by', 'last_updated_by',
            'last_update_login', 'last_update_date', 'creation_date'
        ]

        read_only_fields = [
            'id', 'creation_date', 'created_by'
        ]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sizes
        fields = [
            'menu_item', 'large', 'medium', 'small', 'creation_date', 'created_by', 'last_updated_by',
            'last_update_login', 'last_update_date', 'id'
        ]
        read_only_fields = [
            'id', 'creation_date', 'created_by'
        ]


class LoyaltyPointsSerializer(serializers.Serializer):
    """Serializer for LoyaltyPoints Object"""

    user = 'user.serializers.UserSerializer'

    points = serializers.DecimalField(max_digits=20, decimal_places=2)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    order_date = serializers.DateField()
    order_time = serializers.TimeField()


    def create(self, validated_data):
        """Add points based on order value"""

        user_id = self.context['request'].user
        order_value = validated_data.pop('points', None)

        loyalty_points_percentage = LoyaltyPointsPercentage.objects.first()

        if loyalty_points_percentage:
            points_percentage = loyalty_points_percentage.percentage
        else:
            # If no percentage is found, default to 10%
            points_percentage = Decimal('0.1')

        points_earned = Decimal(order_value) * Decimal(points_percentage)

        loyalty_points_instance, created = LoyaltyPoints.objects.get_or_create(user=user_id)

        if created:
            loyalty_points_instance.points = points_earned
        else:
            loyalty_points_instance.points += points_earned

        loyalty_points_instance.save()

        return loyalty_points_instance


class LoyaltyPointsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyPoints
        fields = [
            'id', 'user', 'points'
        ]
        read_only_fields = [
            'id', 'user'
        ]


class LoyaltyPointsPercentageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyPointsPercentage
        fields = [
            'id', 'percentage', 'creation_date', 'created_by', 'last_updated_by',
            'last_update_login', 'last_update_date'
        ]
        read_only_fields = [
            'id', 'creation_date', 'created_by'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=MenuItems.objects.all())
    item_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItems
        fields = ['item', 'item_name', 'quantity']

    def get_item_name(self, obj):
        return obj.item.name if obj.item else None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitems_set', many=True, read_only=True)

    class Meta:
        model = Orders
        fields = ['amount', 'order_status', 'payment_status', 'items', 'order_date', 'order_time']


class NewOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ['amount', 'order_status', 'payment_status', 'order_date', 'order_time', 'date', 'user']
        read_only_fields = [
            'user'
            ]


class OrderItemsSerializer(serializers.Serializer):
    """Serializer for Order Items Object"""

    user = 'user.serializers.UserSerializer'
    user_name = serializers.CharField(source='order.user.name', read_only=True)
    user_email = serializers.EmailField(source='order.user.email', read_only=True)

    user_id = serializers.IntegerField(required=False)
    order_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    size = serializers.CharField(required=False)
    extras = serializers.ListField(required=False)
    kitchen_notes = serializers.ListField(required=False)
    quantity = serializers.IntegerField(required=False)
    total = serializers.IntegerField(required=False)

    def create(self, validated_data):
        """Create and return a Order Items instance"""
        order_id = validated_data.pop('order_id', None)
        item_id = validated_data.pop('item_id', None)
        size = validated_data.pop('size', None)
        quantity = validated_data.pop('quantity', None)
        extras = validated_data.pop('extras', [])
        kitchen_notes = validated_data.pop('kitchen_notes', [])
        total = validated_data.pop('total', None)

        extras = ",".join(extras)
        kitchen_notes = ",".join(kitchen_notes)

        order_instance = Orders.objects.get(id=order_id)
        item_instance = MenuItems.objects.get(id=item_id)

        orderItems = OrderItems.objects.create(
            order=order_instance,
            item=item_instance,
            size=size,
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
        representation['order_id'] = instance.order.id
        representation['extras'] = instance.extras.split(",") if instance.extras else None
        representation['kitchen_notes'] = instance.kitchen_notes.split(",") if instance.kitchen_notes else None

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


class KitchenNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenNotes
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
    # extras = serializers.ListField(required=False, allow_empty=True)
    # kitchen_notes = serializers.ListField(required=False, allow_empty=True)
    extras_info = serializers.SerializerMethodField()
    kitchen_notes_info = serializers.SerializerMethodField()
    item_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'item_image_url', 'item', 'quantity', 'total', 'extras', 'kitchen_notes', 'size', 'extras_info', 'kitchen_notes_info']
        read_only_fields = ['id', 'user', 'extras_info', 'kitchen_notes_info']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def get_item_name(self, obj):
        cart_items = self.context.get('cart_items', [])
        item = next((item for item in cart_items if item.id == obj.id), None)
        return item.item.name if item else ''

    def get_item_image_url(self, obj):
        return obj.item.image.url if obj.item and obj.item.image else None

    def get_extras_info(self, obj):
        extras_ids = obj.extras.split(',') if obj.extras else []
        extras_info = Extras.objects.filter(pk__in=extras_ids).values('name', 'price')
        return list(extras_info)

    def get_kitchen_notes_info(self, obj):
        kitchen_notes_ids = obj.kitchen_notes.split(',') if obj.kitchen_notes else []
        kitchen_notes_info = KitchenNotes.objects.filter(pk__in=kitchen_notes_ids).values('name', 'price')
        return list(kitchen_notes_info)


class CartItemCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=False)
    size = serializers.CharField(required=False)
    total = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
    extras = serializers.ListField(required=False, allow_empty=True)
    kitchen_notes = serializers.ListField(required=False, allow_empty=True)

    def validate(self, data):
        item_id = data.get('item_id')
        quantity = data.get('quantity')

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")

        return data


class OrderNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderNotifications
        fields = ['id', 'order', 'status']
        read_only_fields = ['id', 'order']
