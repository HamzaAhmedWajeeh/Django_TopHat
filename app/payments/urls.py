from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('payment/order/confirm', views.OrderConfirmation.as_view(), name='order_confirmation'),
    path('payment/intent', views.PaymentIntent.as_view(), name='payment_intent'),
]
