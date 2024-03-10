from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tophat import views

router = DefaultRouter()

router.register('sizes', viewset=views.SizeModelViewSet, basename='sizes')
router.register('kitchen', viewset=views.KitchenNoteModelViewSet, basename='kitchen')


app_name = 'tophat'

urlpatterns = [
    path('categories/', views.CategoriesListAPIView.as_view(), name='categories'),
    path('categories/new/', views.CategoriesCreateAPIView.as_view(), name='categories-new'),
    path('categories/<int:pk>/', views.CategoriesDetailAPIView.as_view(), name='categories-detail'),
    path('categories/delete/<int:pk>/', views.CategoriesDeleteAPIView.as_view(), name='categories-delete'),
    path('categories/update/<int:pk>/', views.CategoriesUpdateAPIView.as_view(), name='categories-update'),

    path('feedback/new/', views.FeedbackCreateAPIView.as_view(), name='feedback-new'),
    path('feedback/all/admin/', views.FeedbackListAPIView.as_view(), name='feedback-all'),
    path('feedback/<int:pk>/', views.FeedbackDetailAPIView.as_view(), name='feedback-detail'),
    path('feedback/delete/<int:pk>/', views.FeedbackDeleteAPIView.as_view(), name='feedback-delete'),

    path('menuitems/', views.MenuItemsListAPIView.as_view(), name='menuitems-list-create'),
    path('menuitems/<int:pk>/', views.MenuItemsRetrieveAPIView.as_view(), name='menuitems-retrieve'),
    path('menuitems/category/<int:category_id>/', views.MenuItemsListByCategoryAPIView.as_view(), name='menuitems-category-all'),
    path('menuitems/update/<int:pk>/', views.MenuItemsUpdateAPIView.as_view(), name='menuitems-update'),
    path('menuitems/delete/<int:pk>/', views.MenuItemsDeleteAPIView.as_view(), name='menuitems-delete'),
    path('menuitems/new/', views.MenuItemsCreateAPIView.as_view(), name='menuitems-delete'),

    path('points/', views.LoyaltyPointsCreation.as_view(), name='loyalty-points-create'),
    path('points/redeem/', views.LoyaltyPointsRedemption.as_view(), name='loyalty-points-redeem'),
    path('points/get/', views.LoyaltyPointsGet.as_view(), name='loyalty-points-get'),

    path('extras/<int:item_id>/', views.ExtrasListByItemView.as_view(), name='extras-item-id'),
    path('extras/delete/<int:item_id>/', views.ExtrasDeleteByItemID.as_view(), name='extras-delete-item-id'),
    path('extras/new/', views.ExtrasPostByItem.as_view(), name='extras-new-item-id'),
    path('extras/update/<int:pk>/', views.ExtrasUpdate.as_view(), name='extras-update'),

    path('cart/add/', views.AddToCartView.as_view(), name='cart-add'),
    path('cart/delete/', views.CartDeleteAll.as_view(), name='cart-delete'),
    path('cart/remove/<int:id>', views.CartDeleteItem.as_view(), name='cart-delete-id'),
    path('cart/update/', views.CartUpdateQuantity.as_view(), name='cart-update'),
    path('cart/get/', views.CartGetView.as_view(), name='cart-get'),

    path('statistics/', views.Statistics.as_view(), name='calculate_statistics'),

    path('order/items/create', views.OrderItemsCreateAPIView.as_view(), name='create-order-items'),

    path('notifications/update/<int:id>', views.NotificationUpdateView.as_view(), name='notifications-update'),
    path('notifications/list', views.NotificationListView.as_view(), name='notifications-list'),

    path('sizes/list/<int:menu_item_id>', views.SizesListView.as_view(), name='sizes-list'),

    path('kitchen/list/<int:menu_item_id>', views.KitchenNoteListView.as_view(), name='kitchen-list'),

    path('', include(router.urls)),
]
