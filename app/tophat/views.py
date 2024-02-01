from rest_framework import (
    generics,
    authentication,
    viewsets
)
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminUser
from core.models import(
    Categories,
)
from .serializers import(
    CategoriesSerializer,
)


class CategoriesListAPIView(generics.ListAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    swagger_schema_title = 'Categories'


class CategoriesDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAuthenticated]
    tags = ['Categories']


class CategoriesUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CategoriesSerializer
    queryset = Categories.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]
    tags = ['Categories']


class CategoriesCreateAPIView(generics.CreateAPIView):
    serializer_class = CategoriesSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsAdminUser]
    tags = ['Categories']
