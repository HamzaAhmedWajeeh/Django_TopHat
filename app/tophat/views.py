from django.shortcuts import get_object_or_404
from rest_framework import (
    generics,
    authentication,
    viewsets,
    status
)
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
    ItemExtras,
    MenuItems,
    LoyaltyPoints
)
from .serializers import(
    CartItemCreateSerializer,
    CartSerializer,
    CategoriesSerializer,
    ExtrasSerializer,
    FeedbackSerializer,
    ItemExtrasSerializer,
    MenuItemsSerializer,
    LoyaltyPointsSerializer,
)
from decimal import Decimal


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


# Menu Items Extras START
class ExtrasListByItemView(generics.ListAPIView):
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        item_id = self.kwargs['item_id']
        return Extras.objects.filter(items=item_id)


class ExtrasDeleteByItemID(generics.DestroyAPIView):
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        item_id = self.kwargs['item_id']

        if not Extras.objects.filter(items=item_id).exists():
            return Response(
                {"message": f"No Extras records found for item_id={item_id}."},
                status=status.HTTP_404_NOT_FOUND
            )

        Extras.objects.filter(items=item_id).delete()

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
    # permission_classes = [IsAuthenticated]

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
    # permission_classes = [IsAuthenticated]

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


class CartGetView(generics.ListAPIView):
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user
        cart_items = Cart.objects.filter(user=user_id)

        self.get_serializer().context['cart_items'] = cart_items  # Store cart_items in context

        return cart_items

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cart_items_data = []

        for item in serializer.data:
            cart_item_data = {
                'item_id': item['id'],
                'item': MenuItems.objects.get(pk=item['item']).name if 'item' in item else '',
                'quantity': item['quantity'],
                'total': item['total']
            }
            cart_items_data.append(cart_item_data)

        return Response(cart_items_data)


class CartUpdateQuantity(generics.UpdateAPIView):
    serializer_class = CartSerializer
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        cart_id = self.kwargs['cart_id']
        new_quantity = request.data.get('quantity')

        try:
            cart_item = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return Response(
                {"message": f"Cart item with id={cart_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if new_quantity is not None and isinstance(new_quantity, int) and new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            return Response(
                {"message": f"Quantity updated for cart item with id={cart_id}."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Invalid quantity. Please provide a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )


class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemCreateSerializer
    authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        item_id = serializer.validated_data['item_id']
        quantity = serializer.validated_data['quantity']

        item = get_object_or_404(MenuItems, pk=item_id)

        total = calculate_total(item.price, quantity)

        cart_item = Cart.objects.filter(user=user, item=item).first()

        if cart_item:
            # Update existing cart item
            cart_item.quantity += quantity
            cart_item.total = calculate_total(item.price, cart_item.quantity)
            cart_item.save()
        else:
            # Create a new cart item
            Cart.objects.create(user=user, item=item, quantity=quantity, total=total)

        cart_items = Cart.objects.filter(user=user)
        cart_data = [{'item': item.item.name, 'quantity': item.quantity, 'total': str(item.total), 'item_id': item_id} for item in cart_items]
        total_price = sum(item.total for item in cart_items)

        return Response({
            "message": "Item added to the cart successfully.",
            "cart": cart_data,
            "total_price": str(total_price),
        }, status=status.HTTP_201_CREATED)