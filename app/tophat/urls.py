from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tophat import views

router = DefaultRouter()

router.register('sizes', viewset=views.SizeModelViewSet, basename='sizes')
router.register('kitchen', viewset=views.KitchenNoteModelViewSet, basename='kitchen')
router.register('sweetner', viewset=views.SweetnerViewset, basename='sweetner')
router.register('order-type', viewset=views.OrderTypeViewSet, basename='order-type')
router.register('instructions', viewset=views.InstructionViewSet, basename='instructions')
router.register('coffee-type', viewset=views.CoffeeTypeViewSet, basename='coffee-type')
router.register('select-base', viewset=views.SelectBaseViewSet, basename='select-base')
router.register('add-replace-ingredients', viewset=views.AddReplaceIngredientsViewSet, basename='add-replace-ingredients')

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

    path('points/redeem/', views.LoyaltyPointsRedemption.as_view(), name='loyalty-points-redeem'),
    path('points/get/', views.LoyaltyPointsGet.as_view(), name='loyalty-points-get'),
    path('points/logic/update', views.LoyaltyPointsPercentageUpdate.as_view(), name='update-points-percentage'),
    path('points/logic/get', views.LoyaltyPointsPercentageGet.as_view(), name='update-points-percentage'),

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

    path('order/history', views.OrderHistory.as_view(), name='order-history-list'),


    path('sizes/list/<int:menu_item_id>', views.SizesListView.as_view(), name='sizes-list'),
    path('sizes/<int:menu_item_id>', views.SizeUpdateDeleteView.as_view(), name='sizes-update-delete'),

    path('kitchen/list/<int:menu_item_id>', views.KitchenNoteListView.as_view(), name='kitchen-list'),

    path('reorder/last/order', views.ReOrderLastOrder.as_view(), name='re-order-last-order'),

    path('alt-milk/list', views.AltMilkList.as_view(), name='alt-milk-list'),
    path('alt-milk/list/<int:menu_item_id>', views.AltMilkListMid.as_view(), name='alt-milk-list-by-item'),
    path('alt-milk/create', views.AltMilkCreate.as_view(), name='alt-milk-create'),
    path('alt-milk/update', views.AltMilkUpdate.as_view(), name='alt-milk-update'),
    path('alt-milk/delete/<int:id>', views.AltMilkDelete.as_view(), name='alt-milk-delete'),

    path('', include(router.urls)),
]
