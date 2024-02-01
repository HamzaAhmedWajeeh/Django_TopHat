from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tophat import views

router = DefaultRouter()

# router.register('categories', viewset=views.CategoriesAPIView)

app_name = 'tophat'

urlpatterns = [
    path('categories/', views.CategoriesListAPIView.as_view(), name='categories'),
    path('categories/new/', views.CategoriesCreateAPIView.as_view(), name='categories-new'),
    path('categories/<int:pk>/', views.CategoriesDetailAPIView.as_view(), name='categories-detail'),
    path('categories/delete/<int:pk>/', views.CategoriesDeleteAPIView.as_view(), name='categories-delete'),
    path('categories/update/<int:pk>/', views.CategoriesUpdateAPIView.as_view(), name='categories-update'),
    path('feedback/', views.FeedbackCreateAPIView.as_view(), name='feedback-new'),
    path('feedback/<int:pk>/', views.FeedbackDetailAPIView.as_view(), name='feedback-detail'),
    path('feedback/delete/<int:pk>/', views.FeedbackDeleteAPIView.as_view(), name='feedback-delete'),
    path('', include(router.urls)),
]
