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
    path('alt-milk/update/<int:id>', views.AltMilkUpdate.as_view(), name='alt-milk-update'),
    path('alt-milk/delete/<int:id>', views.AltMilkDelete.as_view(), name='alt-milk-delete'),

    path('sweetner/list', views.SweetnerList.as_view(), name='sweetner-list'),
    path('sweetner/list/<int:menu_item_id>', views.SweetnerListMid.as_view(), name='sweetner-list-by-item'),
    path('sweetner/create', views.SweetnerCreate.as_view(), name='sweetner-create'),
    path('sweetner/update/<int:id>', views.SweetnerUpdate.as_view(), name='sweetner-update'),
    path('sweetner/delete/<int:id>', views.SweetnerDelete.as_view(), name='sweetner-delete'),

    path('order-type/list', views.OrderTypeList.as_view(), name='order-type-list'),
    path('order-type/list/<int:menu_item_id>', views.OrderTypeListMid.as_view(), name='order-type-list-by-item'),
    path('order-type/create', views.OrderTypeCreate.as_view(), name='order-type-create'),
    path('order-type/update/<int:id>', views.OrderTypeUpdate.as_view(), name='order-type-update'),
    path('order-type/delete/<int:id>', views.OrderTypeDelete.as_view(), name='order-type-delete'),

    path('instructions/list', views.InstructionList.as_view(), name='instructions-list'),
    path('instructions/list/<int:menu_item_id>', views.InstructionListMid.as_view(), name='instructions-list-by-item'),
    path('instructions/create', views.InstructionCreate.as_view(), name='instructions-create'),
    path('instructions/update/<int:id>', views.InstructionUpdate.as_view(), name='instructions-update'),
    path('instructions/delete/<int:id>', views.InstructionDelete.as_view(), name='instructions-delete'),

    path('coffee-type/list', views.CoffeeTypeList.as_view(), name='coffee-type-list'),
    path('coffee-type/list/<int:menu_item_id>', views.CoffeeTypeListMid.as_view(), name='coffee-type-list-by-item'),
    path('coffee-type/create', views.CoffeeTypeCreate.as_view(), name='coffee-type-create'),
    path('coffee-type/update/<int:id>', views.CoffeeTypeUpdate.as_view(), name='coffee-type-update'),
    path('coffee-type/delete/<int:id>', views.CoffeeTypeDelete.as_view(), name='coffee-type-delete'),

    path('select-base/list', views.SelectBaseList.as_view(), name='select-base-list'),
    path('select-base/list/<int:menu_item_id>', views.SelectBaseListMid.as_view(), name='select-base-list-by-item'),
    path('select-base/create', views.SelectBaseCreate.as_view(), name='select-base-create'),
    path('select-base/update/<int:id>', views.SelectBaseUpdate.as_view(), name='select-base-update'),
    path('select-base/delete/<int:id>', views.SelectBaseDelete.as_view(), name='select-base-delete'),

    path('add-replace-ingredients/list', views.AddReplaceIngredientsList.as_view(), name='add-replace-ingredients/list'),
    path('add-replace-ingredients/list/<int:menu_item_id>', views.AddReplaceIngredientsListMid.as_view(), name='add-replace-ingredients/list-by-item'),
    path('add-replace-ingredients/create', views.AddReplaceIngredientsCreate.as_view(), name='add-replace-ingredients/create'),
    path('add-replace-ingredients/update/<int:id>', views.AddReplaceIngredientsUpdate.as_view(), name='add-replace-ingredients/update'),
    path('add-replace-ingredients/delete/<int:id>', views.AddReplaceIngredientsDelete.as_view(), name='add-replace-ingredients/delete'),

    path('', include(router.urls)),
]
