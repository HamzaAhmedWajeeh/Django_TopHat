from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # path('payment/confirm', views.ConfirmPayment.as_view(), name='confirm_payment'),
    path('payment/intent', views.PaymentIntent.as_view(), name='payment_intent'),
]
