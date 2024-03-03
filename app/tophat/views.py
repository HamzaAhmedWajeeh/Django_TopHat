from django.shortcuts import get_object_or_404
from rest_framework import (
    generics,
    authentication,
    viewsets,
    status
)
import json
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal
from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .methods import calculate_total
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
    Sizes
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
    SizeSerializer
)
from decimal import Decimal
from rest_framework.exceptions import ValidationError


# Categories START
class CategoriesListAPIView(generics.ListAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Categories.objects.all().order_by('-creation_date')


class CategoriesDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]


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
    queryset = MenuItems.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class MenuItemsRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = MenuItemsSerializer
    queryset = MenuItems.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]


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
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        category = self.kwargs.get('category_id')
        queryset = MenuItems.objects.filter(category_id=category).all()
        return queryset


# Loyalty Points START
class LoyaltyPointsCreation(generics.CreateAPIView):
    queryset = LoyaltyPoints.objects.all()
    serializer_class = LoyaltyPointsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class LoyaltyPointsRedemption(generics.UpdateAPIView):
    queryset = LoyaltyPoints.objects.all()
    serializer_class = LoyaltyPointsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user_id = self.request.user.id
        points_to_redeem = Decimal(request.data.get('points', 0))

        try:
            loyalty_points_instance = LoyaltyPoints.objects.get(user=user_id)
        except LoyaltyPoints.DoesNotExist:
            return Response({'detail': 'User does not have any loyalty points.'}, status=status.HTTP_400_BAD_REQUEST)

        if loyalty_points_instance.points < points_to_redeem:
            return Response({'detail': 'Not enough points to redeem.'}, status=status.HTTP_400_BAD_REQUEST)

        # Perform additional logic for redeeming points (e.g., apply discount, update order total, etc.)
        # Assuming you have an Order model, you can update it accordingly in this section.

        loyalty_points_instance.points -= points_to_redeem
        loyalty_points_instance.save()

        serializer = self.get_serializer(loyalty_points_instance)
        return Response(serializer.data)


class LoyaltyPointsGet(generics.RetrieveAPIView):
    queryset = LoyaltyPoints.objects.all()
    serializer_class = LoyaltyPointsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve loyalty points for the current authenticated user"""
        user = self.request.user
        loyalty_points_instance = LoyaltyPoints.objects.get(user=user)
        return loyalty_points_instance


# Extras START
class ExtrasListByItemView(generics.ListAPIView):
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

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

        kitchen_notes_prices = {}
        for note_id in kitchen_notes:
            note = KitchenNotes.objects.filter(pk=note_id).first()
            if note:
                kitchen_notes_prices[note_id] = note.price
            else:
                raise ValidationError(f"Kitchen note with ID '{note_id}' is not available.")

        # Calculate total price for the cart item
        total_price = calculate_total_price(price, new_quantity, extras_prices, kitchen_notes_prices)

        # Update extras, size, and kitchen notes if provided
        cart_item.size = size
        cart_item.extras = ','.join(map(str, extras))
        cart_item.kitchen_notes = ','.join(map(str, kitchen_notes))

        cart_item.save()

        # Fetch all cart items again after updating
        cart_items = Cart.objects.filter(user=request.user)
        cart_data = [{'cart_id': item.id, 'item': item.item.name, 'quantity': item.quantity, 'total': str(item.total), 'item_id': item.item.id} for item in cart_items]
        total_price = sum(item.total for item in cart_items)

        return Response(
            {"message": f"Cart item with ID={cart_id} updated successfully.", "cart": cart_data, "total_price": str(total_price)},
            status=status.HTTP_200_OK
        )

def calculate_total_price(base_price, quantity, extras_prices, kitchen_notes_prices):
    total_price = base_price * quantity

    for price in extras_prices.values():
        total_price += price

    for price in kitchen_notes_prices.values():
        total_price += price

    return total_price


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

        total_amount = 0  # Initialize total amount

        # Iterate through each cart item
        for item_data in data:
            # Fetch extras information if extras are present
            if 'extras' in item_data and item_data['extras'] is not None:
                extras_ids = self.parse_int_list(item_data['extras'])
                extras_info = Extras.objects.filter(pk__in=extras_ids).values('name', 'price')
                item_data['extras_info'] = extras_info

            # Fetch kitchen notes information if kitchen notes are present
            if 'kitchen_notes' in item_data and item_data['kitchen_notes'] is not None:
                kitchen_notes_ids = self.parse_int_list(item_data['kitchen_notes'])
                kitchen_notes_info = KitchenNotes.objects.filter(pk__in=kitchen_notes_ids).values('name', 'price')
                item_data['kitchen_notes_info'] = kitchen_notes_info

            total_amount += float(item_data['total'])  # Add total amount to the overall total

        response_data = {
            'cart_items': data,
            'total_amount': '{:.2f}'.format(total_amount)
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def parse_int_list(self, value):
        try:
            if isinstance(value, list):  # Check if value is already a list
                return [int(item.strip()) for item in value if item.strip().isdigit()]
            elif value:
                # Split the string by comma and convert each element to int
                return [int(item.strip()) for item in value.split(',') if item.strip().isdigit()]
            else:
                return []
        except ValueError:
            return []


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

        item = get_object_or_404(MenuItems, pk=item_id)

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

        # Fetch prices of extras and kitchen notes for the new item
        extras_price_total = Decimal('0.0')
        kitchen_notes_price_total = Decimal('0.0')

        if extras_data is not None:
            for extra_id in extras_data:
                extra_price = Extras.objects.filter(pk=extra_id).values_list('price', flat=True).first()
                if extra_price:
                    extras_price_total += extra_price

        if kitchen_notes_data is not None:
            for note_id in kitchen_notes_data:
                note_price = KitchenNotes.objects.filter(pk=note_id).values_list('price', flat=True).first()
                if note_price:
                    kitchen_notes_price_total += note_price

        # Calculate total price including extras and kitchen notes for the new item
        total_price = total + extras_price_total + kitchen_notes_price_total

        # Check if a cart item with the same item ID and size already exists for the user
        existing_cart_item = Cart.objects.filter(
            user=user,
            item=item,
            size=size_name,
            extras=','.join(map(str, extras_data)) if extras_data is not None else None,
            kitchen_notes=','.join(map(str, kitchen_notes_data)) if kitchen_notes_data is not None else None
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
            'size_info': {'name': size_name} if size_name else {}
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
                kitchen_notes=','.join(map(str, kitchen_notes_data)) if kitchen_notes_data is not None else None
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
                'size_info': {'name': size_name} if size_name else {}
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
    serializer_class = OrderSerializer
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


# Re Order last ORDER
class ReOrderLastOrder(generics.GenericAPIView):
    serializer_class = OrderSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user
        last_order = Orders.objects.filter(user=user).order_by('-date').first()

        if not last_order:
            return Response({"error": "No previous order found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve order items from the last order
        last_order_items = OrderItems.objects.filter(order=last_order)

        # Create a new order with the same items
        new_order_data = {
            "user": user,
            "order_date": last_order.order_date,
            "order_time": last_order.order_time,
            "amount": last_order.amount,
            "order_status": "pending",  # or any default status you want for the new order
            "payment_status": "pending",  # or any default status you want for the new order
        }

        new_order_serializer = OrderSerializer(data=new_order_data)
        if new_order_serializer.is_valid():
            new_order = new_order_serializer.save()

            # Create order items for the new order
            for item in last_order_items:
                OrderItems.objects.create(order=new_order, item=item.item, quantity=item.quantity, total=item.total)

            return Response(new_order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            queryset = self.queryset.filter(menu_item=menu_item)
        else:
            queryset = self.queryset
        return queryset
