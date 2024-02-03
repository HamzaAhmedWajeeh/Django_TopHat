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
from core.permissions import IsAdminUser, IsOwnerOrAdmin, IsAdminUserOrReadOnly
from core.models import(
    Categories,
    Extras,
    Feedback,
    ItemExtras,
    MenuItems,
    LoyaltyPoints
)
from .serializers import(
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
    permission_classes = [IsAuthenticated]


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
    permission_classes = [IsAdminUser]


class CategoriesDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CategoriesSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]
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
    permission_classes = [IsAuthenticated]


class MenuItemsDeleteAPIView(generics.DestroyAPIView):
    serializer_class = MenuItemsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = MenuItems.objects.all()

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class MenuItemsCreateAPIView(generics.CreateAPIView):
    serializer_class = MenuItemsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]


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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        item_id = self.kwargs['item_id']
        return Extras.objects.filter(items=item_id)


class ExtrasDeleteByItemID(generics.DestroyAPIView):
    serializer_class = ExtrasSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
