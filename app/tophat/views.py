from django.shortcuts import get_object_or_404
from rest_framework import (
    generics,
    authentication,
    viewsets,
    status
)
from decimal import Decimal
from django.db import connection
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .methods import calculate_total, generate_redemption_id, calculate_total_price
from core.permissions import IsAdminUser, IsOwnerOrAdmin
from core.models import(
    Cart,
    Categories,
    Extras,
    Feedback,
    MenuItems,
    LoyaltyPoints,
    OrderItems,
    Orders,
    KitchenNotes,
    Sizes,
    OrderNotifications,
    User,
    Payments,
    LoyaltyPointsPercentage,
    AddReplaceIngredients,
    AltMilk,
    CoffeeType,
    SelectBase,
    OrderType,
    Sweetner,
    Instructions
)
from .serializers import(
    CartItemCreateSerializer,
    CartSerializer,
    CategoriesSerializer,
    ExtrasSerializer,
    FeedbackSerializer,
    MenuItemsSerializer,
    LoyaltyPointsSerializer,
    OrderSerializer,
    OrderItemsSerializer,
    SizeSerializer,
    OrderNotificationsSerializer,
    KitchenNoteSerializer,
    NewOrderSerializer,
    OrderItemSerializer,
    LoyaltyPointsPercentageSerializer,
    LoyaltyPointsModelSerializer,
    AltMilkSerializer,
    SweetnerSerializer,
    OrderTypeSerializer,
    InstructionsSerializer,
    CoffeeTypeSerializer,
    SelectBaseSerializer,
    AddReplaceIngriedentsSerializer
)
from payments.serializers import PaymentModelSerializer
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Categories START
class CategoriesListAPIView(generics.ListAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Categories.objects.all().order_by('-creation_date')


class CategoriesDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class CategoriesUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]


class CategoriesCreateAPIView(generics.CreateAPIView):
    serializer_class = CategoriesSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class CategoriesDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CategoriesSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = Categories.objects.all()

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# Feedback START
class FeedbackDetailAPIView(generics.RetrieveAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class FeedbackListAPIView(generics.ListAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class FeedbackCreateAPIView(generics.GenericAPIView):
    serializer_class = FeedbackSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        message = request.data.get('message')

        feedback = Feedback.objects.create(user=user, message=message)
        serializer = self.serializer_class(feedback)  # Serialize the feedback object

        return Response(
            serializer.data,  # Use the serialized data in the response
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        user =  request.user

        feedback = Feedback.objects.filter(user=user).all()

        serializer = self.serializer_class(feedback, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FeedbackDeleteAPIView(generics.DestroyAPIView):
    serializer_class = FeedbackSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = Feedback.objects.all()

    def get_queryset(self):
        user = self.request.user
        return Feedback.objects.filter(user=user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({"detail": "Feedback deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        return response


# Menu Items START
class MenuItemsListAPIView(generics.ListAPIView):
    serializer_class = MenuItemsSerializer
    queryset = MenuItems.objects.all().order_by('-id')
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class MenuItemsRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = MenuItemsSerializer
    queryset = MenuItems.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class MenuItemsUpdateAPIView(generics.UpdateAPIView):
    serializer_class = MenuItemsSerializer
    queryset = MenuItems.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class MenuItemsDeleteAPIView(generics.DestroyAPIView):
    serializer_class = MenuItemsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = MenuItems.objects.all()

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class MenuItemsCreateAPIView(generics.CreateAPIView):
    serializer_class = MenuItemsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class MenuItemsListByCategoryAPIView(generics.ListAPIView):
    serializer_class = MenuItemsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        category = self.kwargs.get('category_id')
        queryset = MenuItems.objects.filter(category_id=category).all()
        return queryset


# Loyalty Points START
class LoyaltyPointsCreation(generics.CreateAPIView):
    queryset = LoyaltyPoints.objects.all()
    serializer_class = LoyaltyPointsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class LoyaltyPointsRedemption(generics.UpdateAPIView):
    queryset = LoyaltyPoints.objects.all()
    serializer_class = LoyaltyPointsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        amount = Decimal(request.data.get('amount', 0))
        order_date = request.data.get('order_date')
        order_time = request.data.get('order_time')

        try:
            loyalty_points_instance = LoyaltyPoints.objects.get(user=user.id)
        except LoyaltyPoints.DoesNotExist:
            return Response({'detail': 'User does not have any loyalty points.'}, status=status.HTTP_400_BAD_REQUEST)

        if amount > loyalty_points_instance.points:
            return Response({'detail': 'Not enough points to redeem.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = Cart.objects.filter(user=user)

        order = Orders.objects.create(
            user=user,
            order_date=order_date,
            order_time=order_time,
            amount=amount,
            order_status='pending',
            payment_status='succeeded'
        )

        order_items = []
        for cart_item in cart_items:
            order_item = OrderItems.objects.create(
                order=order,
                item=cart_item.item,
                quantity=cart_item.quantity,
                total=cart_item.total,
                size=cart_item.size,
                kitchen_notes=cart_item.kitchen_notes,
                extras=cart_item.extras
            )
            order_items.append(order_item)

            redemption_id = generate_redemption_id(user_id=user.id, order_date=order_date, order_time=order_time)

        payment = Payments.objects.create(
            payment_intent_id=redemption_id,
            succeeded=True,
            paid_by_points=True,
            order=order,
            user=user,
            created_by=user.id,
            last_updated_by=user.id
        )

        notification = OrderNotifications.objects.create(
            order=order,
            status='pending'
        )

        loyalty_points_instance.points -= amount
        loyalty_points_instance.save()

        order_serializer = NewOrderSerializer(order)
        payment_serializer = PaymentModelSerializer(payment)
        order_item_serializer = OrderItemSerializer(order_items, many=True)

        cart_items.delete()

        subject = "Tophat Coffee - Order Confirmed"
        html_message = render_to_string(
            'payment/invoice.html',
            context={
                'username': user.name, 'user_address': user.address,
                'customer_email': user.email, 'order_date': order.date,
                'user_phone': user.phone, 'user_city': user.city,
                'order_number': order.id, 'amount': order.amount
            }
        )
        send_mail(
            subject,
            message=None,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=user.email,
            html_message=html_message
        )

        return Response({
                'message': 'Order Confirmed - Paid via Loyalty Points',
                'data': {
                    'order_details': order_serializer.data,
                    'order_items': order_item_serializer.data,
                    'loyalty_points': loyalty_points_instance.points,
                    'payment_info': payment_serializer.data,
                }
            }, status=status.HTTP_200_OK)


class LoyaltyPointsGet(generics.RetrieveAPIView):
    serializer_class = LoyaltyPointsModelSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve loyalty points for the current authenticated user"""
        user = self.request.user
        try:
            loyalty_points_instance = LoyaltyPoints.objects.get(user=user)
            return loyalty_points_instance
        except LoyaltyPoints.DoesNotExist:
            return Response({
                'message': 'Loyalty points not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)


class LoyaltyPointsPercentageGet(generics.ListAPIView):
    queryset = LoyaltyPointsPercentage.objects.all()
    serializer_class = LoyaltyPointsPercentageSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class LoyaltyPointsPercentageUpdate(generics.UpdateAPIView):
    queryset = LoyaltyPointsPercentage.objects.all()
    serializer_class = LoyaltyPointsPercentageSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        percentage = Decimal(request.data.get('percentage', 0))

        try:
            loyalty_points_instance = LoyaltyPointsPercentage.objects.first()
            loyalty_points_instance.percentage = percentage
            loyalty_points_instance.save()
            return Response({'message': 'Loyalty points percentage updated successfully.'}, status=status.HTTP_200_OK)
        except LoyaltyPointsPercentage.DoesNotExist:
            return Response({'detail': 'No data found for loyalty points percentage logic'}, status=status.HTTP_400_BAD_REQUEST)


# Extras START
class ExtrasListByItemView(generics.ListAPIView):
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        item_id = self.kwargs['item_id']
        return Extras.objects.filter(menu_item=item_id)


class ExtrasDeleteByItemID(generics.DestroyAPIView):
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        item_id = self.kwargs['item_id']

        if not Extras.objects.filter(menu_item=item_id).exists():
            return Response(
                {"message": f"No Extras records found for item_id={item_id}."},
                status=status.HTTP_404_NOT_FOUND
            )

        Extras.objects.filter(menu_item=item_id).delete()

        return Response(
            {"message": f"All Extras records for item_id={item_id} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class ExtrasPostByItem(generics.CreateAPIView):
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


class ExtrasUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Extras.objects.all()
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]


# CART START
class CartDeleteAll(generics.DestroyAPIView):
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.request.user

        Cart.objects.filter(user=user).delete()

        return Response(
            {"message": "All items deleted from the cart."},
            status=status.HTTP_204_NO_CONTENT
        )


class CartDeleteItem(generics.DestroyAPIView):
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart_id = self.kwargs['id']

        try:
            cart_item = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return Response(
                {"message": f"Cart item with id={cart_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()

        return Response(
            {"message": f"Cart item with id={cart_id} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class CartUpdateQuantity(generics.UpdateAPIView):
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        cart_id = request.data.get('item')
        new_quantity = request.data.get('quantity')
        extras = request.data.get('extras', [])
        kitchen_notes = request.data.get('kitchen_notes', [])
        instructions = request.data.get('instructions', [])
        add_replace_ingredients = request.data.get('add_replace_ingredients', [])
        sweetner = request.data.get('sweetner', [])
        alt_milk = request.data.get('alt_milk', None)
        select_base = request.data.get('select_base', None)
        order_type = request.data.get('order_type', None)
        coffee_type = request.data.get('coffee_type', None)
        size = request.data.get('size')

        # Validate the item ID and new quantity
        if not cart_id or new_quantity is None or not isinstance(new_quantity, int) or new_quantity <= 0:
            raise ValidationError("Invalid request. Please provide a valid item ID and a positive integer quantity.")

        try:
            cart_item = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            raise ValidationError(f"Cart item with id={cart_id} not found.")

        # Fetch the existing quantity and calculate the quantity difference
        old_quantity = cart_item.quantity
        quantity_diff = new_quantity - old_quantity

        # Update the quantity of the cart item
        cart_item.quantity = new_quantity

        # Fetch the item
        item = cart_item.item

        # Fetch prices based on size, extras, and kitchen notes
        if size:
            size_price_field = f"{size.lower()}_price"
            price = getattr(item, size_price_field, None)
            if price is None:
                raise ValidationError(f"The specified size '{size}' is not available for the item.")

        else:
            price = item.price

        extras_prices = {}
        for extra_id in extras:
            extra = Extras.objects.filter(pk=extra_id).first()
            if extra:
                extras_prices[extra_id] = extra.price
            else:
                raise ValidationError(f"Extra with ID '{extra_id}' is not available.")

        add_replace_ingredients_prices = {}
        for add_replace_ingredients_id in add_replace_ingredients:
            add_replace_ingredients = AddReplaceIngredients.objects.filter(pk=add_replace_ingredients_id).first()
            if add_replace_ingredients:
                add_replace_ingredients_prices[add_replace_ingredients_id] = extra.price
            else:
                raise ValidationError(f"add_replace_ingredients with ID '{add_replace_ingredients_id}' is not available.")

        alt_milk_prices = {}
        if alt_milk and alt_milk is not None:
            for alt_milk_id in alt_milk:
                alt_milk = AltMilk.objects.filter(pk=alt_milk_id).first()
                if alt_milk:
                    alt_milk_prices[alt_milk_id] = alt_milk.price
                else:
                    raise ValidationError(f"alt_milk with ID '{alt_milk_id}' is not available.")

        kitchen_notes_prices = {}
        for note_id in kitchen_notes:
            note = KitchenNotes.objects.filter(pk=note_id).first()
            if note:
                kitchen_notes_prices[note_id] = note.price
            else:
                raise ValidationError(f"Kitchen note with ID '{note_id}' is not available.")

        # Calculate total price for the cart item
        total_price = calculate_total_price(price, new_quantity, extras_prices, kitchen_notes_prices, add_replace_ingredients_prices, alt_milk_prices)
        print("Price Calculated: ", total_price)

        # Update extras, size, and kitchen notes if provided
        cart_item.size = size
        cart_item.total = total_price
        cart_item.select_base = select_base if select_base else cart_item.select_base
        cart_item.order_type = order_type if order_type else cart_item.order_type
        cart_item.coffee_type = coffee_type if coffee_type else cart_item.coffee_type
        cart_item.extras = ','.join(map(str, extras))
        cart_item.kitchen_notes = ','.join(map(str, kitchen_notes))
        cart_item.alt_milk = ','.join(map(str, alt_milk)) if alt_milk else cart_item.alt_milk
        cart_item.add_replace_ingredients = ','.join(map(str, add_replace_ingredients)) if add_replace_ingredients else cart_item.add_replace_ingredients
        cart_item.sweetner = ','.join(map(str, sweetner)) if sweetner else cart_item.sweetner
        cart_item.instructions = ','.join(map(str, instructions)) if instructions else cart_item.instructions

        cart_item.save()

        # Fetch all cart items again after updating
        cart_items = Cart.objects.filter(user=request.user)
        cart_data = [{'cart_id': item.id, 'item': item.item.name, 'quantity': item.quantity, 'total': str(item.total), 'item_id': item.item.id} for item in cart_items]
        total_price = sum(item.total for item in cart_items)

        return Response(
            {"message": f"Cart item with ID={cart_id} updated successfully.", "cart": cart_data, "total_price": str(total_price)},
            status=status.HTTP_200_OK
        )


class CartGetView(generics.ListAPIView):
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user
        cart_items = Cart.objects.filter(user=user_id)
        return cart_items

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        total_amount = sum(float(item['total']) for item in data)

        for item_data in data:
            extras_ids = item_data.get('extras')
            kitchen_notes_ids = item_data.get('kitchen_notes')
            alt_milk_ids = item_data.get('alt_milk')
            sweetner_ids = item_data.get('sweetner')
            instructions_ids = item_data.get('instructions')
            add_replace_ingredients_ids = item_data.get('add_replace_ingredients')

            if extras_ids:
                extras_ids = extras_ids.split(',') if ',' in extras_ids else [extras_ids]
                extras_info = [{'name': extra.name, 'price': extra.price} for extra in Extras.objects.filter(pk__in=extras_ids)]
                item_data['extras_info'] = extras_info

            if sweetner_ids:
                sweetner_ids = sweetner_ids.split(',') if ',' in sweetner_ids else [sweetner_ids]
                sweetner_info = [{'type': sweetner.type} for sweetner in Sweetner.objects.filter(pk__in=sweetner_ids)]
                item_data['sweetner_info'] = sweetner_info

            if instructions_ids:
                instructions_ids = instructions_ids.split(',') if ',' in instructions_ids else [instructions_ids]
                instructions_info = [{'type': instructions.type} for instructions in Instructions.objects.filter(pk__in=instructions_ids)]
                item_data['instructions_info'] = instructions_info

            if add_replace_ingredients_ids:
                add_replace_ingredients_ids = add_replace_ingredients_ids.split(',') if ',' in add_replace_ingredients_ids else [add_replace_ingredients_ids]
                add_replace_ingredients_info = [{'type': add_replace_ingredients.type, 'price': add_replace_ingredients.price} for add_replace_ingredients in AddReplaceIngredients.objects.filter(pk__in=add_replace_ingredients_ids)]
                item_data['add_replace_ingredients_info'] = add_replace_ingredients_info

            if alt_milk_ids:
                alt_milk_ids = alt_milk_ids.split(',') if ',' in alt_milk_ids else [alt_milk_ids]
                alt_milk_info = [{'type': alt_milk.type, 'price': alt_milk.price} for alt_milk in AltMilk.objects.filter(pk__in=alt_milk_ids)]
                item_data['alt_milk_info'] = alt_milk_info

            if kitchen_notes_ids:
                kitchen_notes_ids = kitchen_notes_ids.split(',') if ',' in kitchen_notes_ids else [kitchen_notes_ids]
                kitchen_notes_info = [{'name': note.name, 'price': note.price} for note in KitchenNotes.objects.filter(pk__in=kitchen_notes_ids)]
                item_data['kitchen_notes_info'] = kitchen_notes_info

        response_data = {
            'cart_items': data,
            'total_amount': '{:.2f}'.format(total_amount)
        }

        return Response(response_data, status=status.HTTP_200_OK)


class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemCreateSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        item_id = serializer.validated_data['item_id']
        quantity = serializer.validated_data['quantity']
        order_type = serializer.validated_data.get('order_type', None)
        coffee_type = serializer.validated_data.get('coffee_type', None)
        select_base = serializer.validated_data.get('select_base', None)

        item = get_object_or_404(MenuItems, pk=item_id)

        # fetch order_type, coffee_type, select_base
        order_type_obj = OrderType.objects.filter(pk=order_type).first()
        coffee_type_obj = CoffeeType.objects.filter(pk=coffee_type).first()
        select_base_obj = SelectBase.objects.filter(pk=select_base).first()

        # Fetch size data
        size_name = serializer.validated_data.get('size')
        if size_name is not None:
            size_price_field = f"{size_name.lower()}_price"
            price = getattr(item, size_price_field, item.price)
        else:
            price = item.price

        # Calculate total for the main item
        total = calculate_total(price, quantity)

        # Fetch extras and kitchen notes and calculate their total prices
        extras_data = serializer.validated_data.get('extras', None)
        kitchen_notes_data = serializer.validated_data.get('kitchen_notes', None)
        alt_milk_data = serializer.validated_data.get('alt_milk', None)
        sweetner_data = serializer.validated_data.get('sweetner', None)
        instructions_data = serializer.validated_data.get('instructions', None)
        add_replace_ingredients_data = serializer.validated_data.get('add_replace_ingredients', None)

        # Fetch prices of extras and kitchen notes for the new item
        extras_price_total = Decimal('0.0')
        kitchen_notes_price_total = Decimal('0.0')
        alt_milk_price_total = Decimal('0.0')
        add_replace_ingredients_price_total = Decimal('0.0')

        if extras_data is not None:
            for extra_id in extras_data:
                extra_price = Extras.objects.filter(pk=extra_id).values_list('price', flat=True).first()
                if extra_price:
                    extras_price_total += extra_price

        if add_replace_ingredients_data is not None:
            for add_replace_ingredients_id in add_replace_ingredients_data:
                add_replace_ingredients_price = Extras.objects.filter(pk=add_replace_ingredients_id).values_list('price', flat=True).first()
                if add_replace_ingredients_price:
                    add_replace_ingredients_price_total += add_replace_ingredients_price

        if alt_milk_data is not None:
            for alt_milk_id in alt_milk_data:
                alt_milk_price = AltMilk.objects.filter(pk=alt_milk_id).values_list('price', flat=True).first()
                if alt_milk_price:
                    alt_milk_price_total += alt_milk_price

        if kitchen_notes_data is not None:
            for note_id in kitchen_notes_data:
                note_price = KitchenNotes.objects.filter(pk=note_id).values_list('price', flat=True).first()
                if note_price:
                    kitchen_notes_price_total += note_price

        # Calculate total price including extras and kitchen notes for the new item
        total_price = total + extras_price_total + kitchen_notes_price_total + add_replace_ingredients_price_total + alt_milk_price_total

        # Check if a cart item with the same item ID and size already exists for the user
        existing_cart_item = Cart.objects.filter(
            user=user,
            item=item,
            size=size_name,
            extras=','.join(map(str, extras_data)) if extras_data is not None else None,
            kitchen_notes=','.join(map(str, kitchen_notes_data)) if kitchen_notes_data is not None else None,
            order_type=order_type,
            coffee_type=coffee_type,
            select_base=select_base,
            sweetner=','.join(map(str, sweetner_data)) if sweetner_data is not None else None,
            instructions=','.join(map(str, instructions_data)) if instructions_data is not None else None,
            alt_milk=','.join(map(str, alt_milk_data)) if alt_milk_data is not None else None,
            add_replace_ingredients=','.join(map(str, add_replace_ingredients_data)) if add_replace_ingredients_data is not None else None,

        ).first()

        if existing_cart_item is not None:
            # Update existing cart item
            existing_cart_item.quantity += quantity
            existing_cart_item.total += total_price
            existing_cart_item.save()

            cart_data = [{
                'cart_id': existing_cart_item.id if existing_cart_item else None,
                'item': item.name,
                'quantity': existing_cart_item.quantity,
                'total': str(total_price),
                'item_id': item_id,
                'extras_info': ','.join(str(extra) for extra in Extras.objects.filter(pk__in=extras_data).values('name', 'price')) if extras_data is not None else None,
                'kitchen_notes_info': ','.join(str(note) for note in KitchenNotes.objects.filter(pk__in=kitchen_notes_data).values('name', 'price')) if kitchen_notes_data is not None else None,
                'instructions_info': ','.join(str(instructions) for instructions in Instructions.objects.filter(pk__in=instructions_data).values('type')) if instructions_data is not None else None,
                'add_replace_ingredients_info': ','.join(str(add_replace_ingredients) for add_replace_ingredients in AddReplaceIngredients.objects.filter(pk__in=add_replace_ingredients_data).values('type', 'price')) if add_replace_ingredients_data is not None else None,
                'alt_milk_info': ','.join(str(alt_milk) for alt_milk in AltMilk.objects.filter(pk__in=alt_milk_data).values('type', 'price')) if alt_milk_data is not None else None,
                'size_info': {'name': size_name} if size_name else {},
                'order_type_info': {'name': order_type_obj.type} if order_type_obj else {},  # Serialize the name
                'coffee_type_info': {'name': coffee_type_obj.type} if coffee_type_obj else {},  # Serialize the name
                'select_base_info': {'name': select_base_obj.type} if select_base_obj else {}  # Serialize the name
            }]

        else:
            # Create a new cart item with the extras and kitchen notes associated with the new item only
            new_cart = Cart.objects.create(
                user=user,
                item=item,
                quantity=quantity,
                total=total_price,
                size=size_name,
                extras=','.join(map(str, extras_data)) if extras_data is not None else None,
                kitchen_notes=','.join(map(str, kitchen_notes_data)) if kitchen_notes_data is not None else None,
                order_type=order_type,
                coffee_type=coffee_type,
                select_base=select_base,
                sweetner=','.join(map(str, sweetner_data)) if sweetner_data is not None else None,
                instructions=','.join(map(str, instructions_data)) if instructions_data is not None else None,
                alt_milk=','.join(map(str, alt_milk_data)) if alt_milk_data is not None else None,
                add_replace_ingredients=','.join(map(str, add_replace_ingredients_data)) if add_replace_ingredients_data is not None else None,
            )

            # Fetch details only for the newly added item
            cart_data = [{
                'cart_id': new_cart.id if new_cart else None,
                'item': item.name,
                'quantity': quantity,
                'total': str(total_price),
                'item_id': item_id,
                'extras_info': ','.join(str(extra) for extra in Extras.objects.filter(pk__in=extras_data).values('name', 'price')) if extras_data is not None else None,
                'kitchen_notes_info': ','.join(str(note) for note in KitchenNotes.objects.filter(pk__in=kitchen_notes_data).values('name', 'price')) if kitchen_notes_data is not None else None,
                'size_info': {'name': size_name} if size_name else {},
                'instructions_info': ','.join(str(instructions) for instructions in Instructions.objects.filter(pk__in=instructions_data).values('type')) if instructions_data is not None else None,
                'add_replace_ingredients_info': ','.join(str(add_replace_ingredients) for add_replace_ingredients in AddReplaceIngredients.objects.filter(pk__in=add_replace_ingredients_data).values('type', 'price')) if add_replace_ingredients_data is not None else None,
                'alt_milk_info': ','.join(str(alt_milk) for alt_milk in AltMilk.objects.filter(pk__in=alt_milk_data).values('type', 'price')) if alt_milk_data is not None else None,
                'order_type_info': {'name': order_type_obj.type} if order_type_obj else {},  # Serialize the name
                'coffee_type_info': {'name': coffee_type_obj.type} if coffee_type_obj else {},  # Serialize the name
                'select_base_info': {'name': select_base_obj.type} if select_base_obj else {}  # Serialize the name
            }]

        return Response({
            "message": "Item added to the cart successfully.",
            "cart": cart_data,
            "total_price": str(total_price),
        }, status=status.HTTP_201_CREATED)


# Statistics for Admin
class GetDataBase(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    @staticmethod
    def fillna_based_on_dtype(df):
        for col in df.columns:
            if df[col].dtype == "float64":
                df[col].fillna(-1.0, inplace=True)
            elif df[col].dtype == "object":
                df[col].fillna("unavilable", inplace=True)
            elif df[col].dtype == "int64":
                df[col].fillna(-1, inplace=True)
            elif df[col].dtype == "bool":
                df[col].fillna(False, inplace=True)
        return df


class Statistics(GetDataBase):
    serializer_class = CartItemCreateSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        query = """
            SELECT
    COUNT(DISTINCT o.id) AS total_orders,
    SUM(o.amount) AS total_sales,
    (SELECT COUNT(DISTINCT id) FROM core_user WHERE verified = 1 AND is_staff = 0) AS total_verified_users
FROM
    core_orders o
INNER JOIN
    core_user u ON o.user_id = u.id
WHERE
    u.verified = 1 AND u.is_staff = 0;

        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            total_orders = row[0]
            total_sales = row[1]
            total_users = row[2]

        data = {
            "total_orders": total_orders,
            "total_sales": total_sales,
            "total_verified_users": total_users
        }
        return Response(data, status=status.HTTP_200_OK)


class OrderHistory(generics.ListAPIView):
    serializer_class = None
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Orders.objects.filter(
            user=user,
            order_status='completed',
            payment_status='succeeded'
        )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Separate orders into two categories: PAID BY POINTS and PAID ONLINE
        paid_by_points_orders = queryset.filter(payments__paid_by_points=True)
        paid_online_orders = queryset.exclude(payments__paid_by_points=True)

        # Serialize orders and order items for both categories
        paid_by_points_serializer = OrderSerializer(paid_by_points_orders, many=True)
        paid_online_serializer = OrderSerializer(paid_online_orders, many=True)

        # Return response
        return Response({
            'paid_by_points_orders': paid_by_points_serializer.data,
            'paid_online_orders': paid_online_serializer.data
        }, status=status.HTTP_200_OK)


# Re Order last ORDER
class ReOrderLastOrder(generics.ListAPIView):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        last_order = Orders.objects.filter(user=user).order_by('-date').first()

        if not last_order or last_order == [] or last_order is None:
            return Response({"error": "No previous order found."}, status=status.HTTP_404_NOT_FOUND)

        last_order_items = OrderItems.objects.filter(order=last_order)

        if not last_order_items or last_order_items == [] or last_order_items is None:
            return Response({
                "message": "No order items found in your previous order",
            }, status=status.HTTP_404_NOT_FOUND)

        # Delete existing items in the cart for the user
        Cart.objects.filter(user=user).delete()

        # Add order items to the cart
        for item in last_order_items:
            Cart.objects.create(
                user=user,
                item=item.item,
                quantity=item.quantity,
                total=item.total,
                size=item.size,
                kitchen_notes=item.kitchen_notes,
                extras=item.extras
            )

        # Fetch cart items after updating the cart
        cart_items = Cart.objects.filter(user=user)
        cart_serializer = self.serializer_class(cart_items, many=True)

        return Response({
            "message": "Cart updated with items from the last order.",
            "cart_items": cart_serializer.data
        }, status=status.HTTP_200_OK)


class OrderItemsCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderItemsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


# Sizes
class SizeModelViewSet(viewsets.ModelViewSet):
    serializer_class = SizeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Sizes.objects.all()

    def get_queryset(self):
        menu_item = self.kwargs.get('menu_item')
        if menu_item:
            queryset = self.queryset.filter(menu_item_id=menu_item)
        else:
            queryset = self.queryset
        return queryset


class SizesListView(generics.ListAPIView):
    serializer_class = SizeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        return Sizes.objects.filter(menu_item_id=menu_item_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        menu_item_id = self.kwargs.get('menu_item_id')
        try:
            menu_item = MenuItems.objects.get(id=menu_item_id)
        except MenuItems.DoesNotExist:
            return Response({'message': 'Menu item does not exist'}, status=404)

        # Initialize the list to store size data
        size_data = []

        # Iterate through each size in the queryset
        for size_item in queryset:
            # Determine the size name
            large = True if size_item.large == True else False
            size_name = 'Large'
            price_field = 'large_price'
            if large == True:
                print(size_name)
                price = getattr(menu_item, price_field, None)
                if price is not None:
                    size_data.append({
                        'name': size_name,
                        'price': price
                    })
            medium = True if size_item.medium == True else False
            size_name = 'Medium'
            price_field = 'medium_price'
            if medium == True:
                print(size_name)
                price = getattr(menu_item, price_field, None)
                if price is not None:
                    size_data.append({
                        'name': size_name,
                        'price': price
                    })
            small = True if size_item.small == True else False
            size_name = 'Small'
            price_field = 'small_price'
            if small == True:
                print(size_name)
                price = getattr(menu_item, price_field, None)
                if price is not None:
                    size_data.append({
                        'name': size_name,
                        'price': price
                    })

        response_data = {
            'sizes': size_data
        }
        return Response(response_data)


class SizeUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SizeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'menu_item_id'

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        return Sizes.objects.filter(menu_item=menu_item_id)


# Kitchen Notes
class KitchenNoteModelViewSet(viewsets.ModelViewSet):
    serializer_class = KitchenNoteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = KitchenNotes.objects.all()

    def get_queryset(self):
        menu_item = self.kwargs.get('menu_item_id')
        if menu_item:
            queryset = self.queryset.filter(menu_item_id=menu_item)
        else:
            queryset = self.queryset
        return queryset


class KitchenNoteListView(generics.ListAPIView):
    serializer_class = KitchenNoteSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        return KitchenNotes.objects.filter(menu_item_id=menu_item_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class NotificationUpdateView(generics.UpdateAPIView):
    serializer_class = OrderNotificationsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = OrderNotifications.objects.all()
    lookup_field = 'id'

    def perform_update(self, serializer):
        instance = serializer.save()
        if 'status' in serializer.validated_data:
            new_status = serializer.validated_data['status']
            order_notification = instance
            order = order_notification.order
            order.order_status = new_status
            order.save()


class NotificationListView(generics.ListAPIView):
    serializer_class = OrderNotificationsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = OrderNotifications.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        orders_and_items = []

        for notification in queryset:
            order_id = notification.order_id
            order = Orders.objects.get(id=order_id)
            order_items = OrderItems.objects.filter(order=order_id)
            user = User.objects.get(pk=order.user_id)

            order_data = {
                'notification': OrderNotificationsSerializer(notification).data,
                'order': NewOrderSerializer(order).data,
                'user': {
                    'id': user.id,
                    'username': user.name,
                    'email': user.email,
                    'address': user.address,
                    'phone': user.phone
                },
                'order_items': [],
            }

            for order_item in order_items:
                menu_item = MenuItems.objects.get(pk=order_item.item_id)

                # Retrieve Extras instances
                extras_list = []
                for extra_id in order_item.extras.split(",") if order_item.extras else []:
                    extra = Extras.objects.get(pk=int(extra_id))
                    extras_list.append({'name': extra.name, 'price': extra.price})

                # Retrieve KitchenNotes instances
                kitchen_notes_list = []
                for kitchen_note_id in order_item.kitchen_notes.split(",") if order_item.kitchen_notes else []:
                    kitchen_note = KitchenNotes.objects.get(pk=int(kitchen_note_id))
                    kitchen_notes_list.append({'name': kitchen_note.name})


                item_data = {
                    'item': {
                        'name': menu_item.name,
                        'description': menu_item.description
                    },
                    'extras': extras_list,
                    'kitchen_notes': kitchen_notes_list,
                    'quantity': order_item.quantity,
                    'total': order_item.total,
                    'size': order_item.size
                }
                order_data['order_items'].append(item_data)

            orders_and_items.append(order_data)

        return Response(orders_and_items)


# Alternate Milk
class AltMilkList(generics.ListAPIView):
    serializer_class = AltMilkSerializer
    queryset = AltMilk.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class AltMilkListMid(generics.ListAPIView):
    serializer_class = AltMilkSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        queryset = AltMilk.objects.filter(item=menu_item_id).all()
        return queryset


class AltMilkCreate(generics.CreateAPIView):
    serializer_class = AltMilkSerializer
    queryset = AltMilk.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class AltMilkUpdate(generics.UpdateAPIView):
    serializer_class = AltMilkSerializer
    queryset = AltMilk.objects.all()
    lookup_field = 'id'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class AltMilkDelete(generics.DestroyAPIView):
    serializer_class = AltMilkSerializer
    queryset = AltMilk.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not AltMilk.objects.filter(id=id).exists():
            return Response(
                {"message": f"No AltMilk records found for id = {id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        AltMilk.objects.filter(id=id).delete()

        return Response(
            {"message": f"AltMilk record deleted at id={id}."},
            status=status.HTTP_204_NO_CONTENT
        )


# Sweetner
class SweetnerList(generics.ListAPIView):
    serializer_class = SweetnerSerializer
    queryset = Sweetner.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class SweetnerListMid(generics.ListAPIView):
    serializer_class = SweetnerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        queryset = Sweetner.objects.filter(item=menu_item_id).all()
        return queryset


class SweetnerCreate(generics.CreateAPIView):
    serializer_class = SweetnerSerializer
    queryset = Sweetner.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class SweetnerUpdate(generics.UpdateAPIView):
    serializer_class = SweetnerSerializer
    queryset = Sweetner.objects.all()
    lookup_field = 'id'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class SweetnerDelete(generics.DestroyAPIView):
    serializer_class = SweetnerSerializer
    queryset = Sweetner.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not Sweetner.objects.filter(id=id).exists():
            return Response(
                {"message": f"No Sweetner records found for id = {id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        Sweetner.objects.filter(id=id).delete()

        return Response(
            {"message": f"AltMilk record deleted at id={id}."},
            status=status.HTTP_204_NO_CONTENT
        )


# OrderType
class OrderTypeList(generics.ListAPIView):
    serializer_class = OrderTypeSerializer
    queryset = OrderType.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class OrderTypeListMid(generics.ListAPIView):
    serializer_class = OrderTypeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        queryset = OrderType.objects.filter(item=menu_item_id).all()
        return queryset


class OrderTypeCreate(generics.CreateAPIView):
    serializer_class = OrderTypeSerializer
    queryset = OrderType.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class OrderTypeUpdate(generics.UpdateAPIView):
    serializer_class = OrderTypeSerializer
    queryset = OrderType.objects.all()
    lookup_field = 'id'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class OrderTypeDelete(generics.DestroyAPIView):
    serializer_class = OrderTypeSerializer
    queryset = OrderType.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not OrderType.objects.filter(id=id).exists():
            return Response(
                {"message": f"No OrderType records found for id = {id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        OrderType.objects.filter(id=id).delete()

        return Response(
            {"message": f"OrderType record deleted at id={id}."},
            status=status.HTTP_204_NO_CONTENT
        )


# Instructions
class InstructionList(generics.ListAPIView):
    serializer_class = InstructionsSerializer
    queryset = Instructions.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class InstructionListMid(generics.ListAPIView):
    serializer_class = InstructionsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        queryset = Instructions.objects.filter(item=menu_item_id).all()
        return queryset


class InstructionCreate(generics.CreateAPIView):
    serializer_class = InstructionsSerializer
    queryset = Instructions.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class InstructionUpdate(generics.UpdateAPIView):
    serializer_class = InstructionsSerializer
    queryset = Instructions.objects.all()
    lookup_field = 'id'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class InstructionDelete(generics.DestroyAPIView):
    serializer_class = InstructionsSerializer
    queryset = Instructions.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not Instructions.objects.filter(id=id).exists():
            return Response(
                {"message": f"No Instructions records found for id = {id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        Instructions.objects.filter(id=id).delete()

        return Response(
            {"message": f"Instructions record deleted at id={id}."},
            status=status.HTTP_204_NO_CONTENT
        )


# CoffeType
class CoffeeTypeList(generics.ListAPIView):
    serializer_class = CoffeeTypeSerializer
    queryset = CoffeeType.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class CoffeeTypeListMid(generics.ListAPIView):
    serializer_class = CoffeeTypeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        queryset = CoffeeType.objects.filter(item=menu_item_id).all()
        return queryset


class CoffeeTypeCreate(generics.CreateAPIView):
    serializer_class = CoffeeTypeSerializer
    queryset = CoffeeType.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class CoffeeTypeUpdate(generics.UpdateAPIView):
    serializer_class = CoffeeTypeSerializer
    queryset = CoffeeType.objects.all()
    lookup_field = 'id'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class CoffeeTypeDelete(generics.DestroyAPIView):
    serializer_class = CoffeeTypeSerializer
    queryset = CoffeeType.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not CoffeeType.objects.filter(id=id).exists():
            return Response(
                {"message": f"No CoffeeType records found for id = {id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        CoffeeType.objects.filter(id=id).delete()

        return Response(
            {"message": f"CoffeeType record deleted at id={id}."},
            status=status.HTTP_204_NO_CONTENT
        )


# SelectBase
class SelectBaseList(generics.ListAPIView):
    serializer_class = SelectBaseSerializer
    queryset = SelectBase.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class SelectBaseListMid(generics.ListAPIView):
    serializer_class = SelectBaseSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        queryset = SelectBase.objects.filter(item=menu_item_id).all()
        return queryset


class SelectBaseCreate(generics.CreateAPIView):
    serializer_class = SelectBaseSerializer
    queryset = SelectBase.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class SelectBaseUpdate(generics.UpdateAPIView):
    serializer_class = SelectBaseSerializer
    queryset = SelectBase.objects.all()
    lookup_field = 'id'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class SelectBaseDelete(generics.DestroyAPIView):
    serializer_class = SelectBaseSerializer
    queryset = SelectBase.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not SelectBase.objects.filter(id=id).exists():
            return Response(
                {"message": f"No SelectBase records found for id = {id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        SelectBase.objects.filter(id=id).delete()

        return Response(
            {"message": f"SelectBase record deleted at id={id}."},
            status=status.HTTP_204_NO_CONTENT
        )


# AddReplaceIngredients
class AddReplaceIngredientsList(generics.ListAPIView):
    serializer_class = AddReplaceIngriedentsSerializer
    queryset = AddReplaceIngredients.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]


class AddReplaceIngredientsListMid(generics.ListAPIView):
    serializer_class = AddReplaceIngriedentsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        queryset = AddReplaceIngredients.objects.filter(item=menu_item_id).all()
        return queryset


class AddReplaceIngredientsCreate(generics.CreateAPIView):
    serializer_class = AddReplaceIngriedentsSerializer
    queryset = AddReplaceIngredients.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class AddReplaceIngredientsUpdate(generics.UpdateAPIView):
    serializer_class = AddReplaceIngriedentsSerializer
    queryset = AddReplaceIngredients.objects.all()
    lookup_field = 'id'
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]


class AddReplaceIngredientsDelete(generics.DestroyAPIView):
    serializer_class = AddReplaceIngriedentsSerializer
    queryset = AddReplaceIngredients.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not AddReplaceIngredients.objects.filter(id=id).exists():
            return Response(
                {"message": f"No AddReplaceIngredients records found for id = {id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        AddReplaceIngredients.objects.filter(id=id).delete()

        return Response(
            {"message": f"AddReplaceIngredients record deleted at id={id}."},
            status=status.HTTP_204_NO_CONTENT
        )
