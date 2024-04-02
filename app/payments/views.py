import stripe
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from core.models import (Payments, Orders, OrderItems, Cart, OrderNotifications, LoyaltyPoints)
from tophat.serializers import OrderSerializer, OrderItemSerializer
from .serializers import PaymentSerializer, PaymentIntentSerializer
from tophat.functions import calculateLoyaltyPoints


class CreatePayment(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PaymentSerializer

    def post(self, request):
        user = self.request.user
        request_data = request.data
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            with transaction.atomic():
                cart_items = Cart.objects.filter(user=user)
                total_amount = sum(cart_item.total for cart_item in cart_items)

                customer = stripe.Customer.list(email=user.email).data
                if not customer:
                    customer = stripe.Customer.create(
                        name=user.name,
                        email=user.email,
                        payment_method=request_data['payment_method_id']
                    )
                else:
                    customer = customer[0]

                order = Orders.objects.create(
                    user=user,
                    order_date=request_data.get('order_date'),
                    order_time=request_data.get('order_time'),
                    amount=total_amount,
                    order_status='pending',
                    payment_status='pending'
                )

                order_items = []
                for cart_item in cart_items:
                    order_item = OrderItems.objects.create(
                        order=order,
                        item=cart_item.item,
                        quantity=cart_item.quantity,
                        total=cart_item.total,
                        size=cart_item.size,
                        kitchen_notes=cart_item.kitchen_notes,
                        extras=cart_item.extras
                    )
                    order_items.append(order_item)

                payment_intent = stripe.PaymentIntent.create(
                    customer=customer,
                    payment_method=request_data['payment_method_id'],
                    currency='aud',
                    amount=int(total_amount * 100),
                    confirm=True,
                    return_url="http://localhost:9001/",
                    receipt_email=user.email
                )

                payment = Payments.objects.create(
                    payment_intent_id=payment_intent.id,
                    succeeded=payment_intent.status == 'succeeded',
                    order=order,
                    user=user,
                    created_by=user,
                    last_updated_by=user,
                    last_update_login=user,
                )

                order.payment_status = 'succeeded'
                order.save()

                notification = OrderNotifications.objects.create(
                    order=order,
                    status='pending'
                )

                loyalty_points = calculateLoyaltyPoints(total_amount)

                loyalty_points_instance = LoyaltyPoints.objects.create(
                    user=user,
                    points=loyalty_points
                )

                cart_items.delete()

            return Response({
                'message': 'Order Confirmed',
                'data': {
                    'order_details': OrderSerializer(order).data,
                    'order_items': OrderItemSerializer(order_items, many=True).data,
                    'loyalty_points': loyalty_points_instance.points,
                }
            }, status=status.HTTP_200_OK)

        except stripe.error.CardError as e:
            message = str(e)
            if ":" in message:
                message = message.split(": ")[1]
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f"Error processing payment: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentIntent(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PaymentIntentSerializer

    def post(self, request):
        user = self.request.user
        request_data = request.data
        stripe.api_key = settings.STRIPE_SECRET_KEY

        cart_items = Cart.objects.filter(user=user)
        total_amount = sum(cart_item.total for cart_item in cart_items)

        total_returned_amount = request_data.get('amount', total_amount)
        total_returned_amount_float = float(total_returned_amount)
        total_returned_amount_integer = int(total_returned_amount_float * 100)

        customer = stripe.Customer.list(email=user.email).data
        if not customer:
            customer = stripe.Customer.create(
                name=user.name,
                email=user.email
            )
        else:
            customer = customer[0]

        ephemeralKey = stripe.EphemeralKey.create(
            customer=customer['id'],
            stripe_version='2023-10-16'
        )

        payment_intent = stripe.PaymentIntent.create(
                    customer=customer['id'],
                    currency='aud',
                    amount=total_returned_amount_integer,
                    receipt_email=user.email,
                )

        return Response({

                'paymentIntent': payment_intent.client_secret,
                'customerID': customer.id,
                'customerEmail': customer.email,
                'customerName': customer.name,
                'ephemeralKey': ephemeralKey.secret,
                'paymentIntentID': payment_intent.id

            }, status=status.HTTP_200_OK)


class OrderConfirmation(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PaymentSerializer

    def post(self, request):
        user = self.request.user
        request_data = request.data

        with transaction.atomic():
            cart_items = Cart.objects.filter(user=user)
            total_amount = sum(cart_item.total for cart_item in cart_items)
            amount_returned = request_data.get('amount')
            payment_intent = request_data.get('payment_intent_id')

            order = Orders.objects.create(
                user=user,
                order_date=request_data.get('order_date'),
                order_time=request_data.get('order_time'),
                amount=amount_returned,
                order_status='pending',
                payment_status='succeeded'
            )

            order_items = []
            for cart_item in cart_items:
                order_item = OrderItems.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    total=cart_item.total,
                    size=cart_item.size,
                    kitchen_notes=cart_item.kitchen_notes,
                    extras=cart_item.extras
                )
                order_items.append(order_item)

            payment = Payments.objects.create(
                payment_intent_id=payment_intent,
                succeeded=True,
                order=order,
                user=user,
                created_by=user.id,
                last_updated_by=user.id
            )

            notification = OrderNotifications.objects.create(
                order=order,
                status='pending'
            )

            loyalty_points = calculateLoyaltyPoints(amount_returned)

            loyalty_points_instance = LoyaltyPoints.objects.create(
                user=user,
                points=loyalty_points
            )

            cart_items.delete()

            return Response({
                'message': 'Order Confirmed',
                'data': {
                    'order_details': OrderSerializer(order).data,
                    'order_items': OrderItemSerializer(order_items, many=True).data,
                    'loyalty_points': loyalty_points_instance.points,
                }
            }, status=status.HTTP_200_OK)

