from rest_framework import (
    generics,
    authentication,
    viewsets,
    status
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminUser, IsOwnerOrAdmin
from core.models import(
    Categories,
    Feedback
)
from .serializers import(
    CategoriesSerializer,
    FeedbackSerializer
)


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
    permission_classes = [IsAuthenticated]


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
    permission_classes = [IsOwnerOrAdmin]
    queryset = Feedback.objects.all()

    def get_queryset(self):
        user = self.request.user
        return Feedback.objects.filter(user=user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({"detail": "Feedback deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        return response
