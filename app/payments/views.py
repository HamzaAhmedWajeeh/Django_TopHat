import os
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.conf import settings
import stripe
from core.models import(
    Payments,
    Orders,
    OrderItems,
    Cart,
    OrderNotifications
)
from tophat.serializers import OrderSerializer, OrderItemSerializer
from django.db import transaction

# class CreatePayment(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     serializer_class = OrderSerializer

#     def post(self, request):
#         order_serializer = self.get_serializer(data=request.data)
#         if not order_serializer.is_valid():
#             return Response(
#                 {'message': order_serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         order_data = order_serializer.validated_data
#         user = self.request.user
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         # data = request.data
#         # print(data)
#         # payment_method_id = data['payment_method_id']
#         items_data = order_data.get('items', [])
#         print(items_data)

#         total_amount = sum(item['quantity'] * item['item'].price for item in items_data)
#         print(total_amount)

#         try:
#             with transaction.atomic():
#                 # Try to retrieve the customer, create if not exists
#                 customer_data = stripe.Customer.list(email=user.email).data
#                 if len(customer_data) == 0:
#                     customer = stripe.Customer.create(
#                         name=user.name,
#                         email=user.email,
#                     )
#                 else:
#                     customer = customer_data[0]

#                 payment_intent = stripe.PaymentIntent.create(
#                     customer=customer.id,
#                     currency='aud',
#                     amount=int(total_amount * 100),
#                     confirm=True,
#                     return_url="http://localhost:9001/",
#                     receipt_email=user.email
#                 )

#                 order = Orders.objects.create(
#                     user=user,
#                     amount=total_amount,
#                     order_status='Pending',
#                     payment_status='Unpaid'
#                 )

#                 for item_data in items_data:
#                     item = item_data['item']
#                     quantity = item_data['quantity']
#                     total = item['price'] * quantity
#                     OrderItems.objects.create(
#                         order=order,
#                         item=item,
#                         quantity=quantity,
#                         total=total
#                     )

#                 payment = Payments.objects.create(
#                     order=order,
#                     user=user,
#                     succeeded=payment_intent.status == 'succeeded',
#                     payment_intent_id=payment_intent.id
#                 )

#                 return Response(
#                     status=status.HTTP_200_OK,
#                     data={
#                         'message': 'Success',
#                         'data': {'customer_id': customer.id},
#                         'payment': {
#                             'id': payment.id,
#                             'organization': user.organization.name
#                         }
#                     }
#                 )
#         except stripe.error.CardError as e:
#             message = str(e)
#             if ":" in message:
#                 message = message.split(": ")[1]
#             return Response(
#                 {'message': message},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             # Handle other exceptions (e.g., network issues, API errors) here
#             return Response(
#                 {'message': f"Error processing payment: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


class CreatePayment(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = OrderSerializer

    def post(self, request):
        user = self.request.user
        data = request.data
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            with transaction.atomic():
                # Fetch all cart items for the user
                cart_items = Cart.objects.filter(user=user)

                # Calculate total amount from cart items
                total_amount = sum(cart_item.total for cart_item in cart_items)

                # Retrieve or create Stripe customer
                customer = stripe.Customer.list(email=user.email).data
                if not customer:
                    customer = stripe.Customer.create(
                        name=user.name,
                        email=user.email,
                        payment_method=data['payment_method_id']
                    )
                else:
                    customer = customer[0]

                # Create order
                order = Orders.objects.create(
                    user=user,
                    order_date=data.get('order_date'),
                    order_time=data.get('order_time'),
                    amount=total_amount,
                    order_status='pending',
                    payment_status='pending'
                )

                # Save order items
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


                # Create payment intent
                payment_intent = stripe.PaymentIntent.create(
                    customer=customer,
                    payment_method=data['payment_method_id'],
                    currency='aud',
                    amount=int(total_amount * 100),
                    confirm=True,
                    return_url="http://localhost:9001/",
                    receipt_email=user.email
                )

                # Save payment details
                payment = Payments.objects.create(
                    payment_intent_id=payment_intent.id,
                    succeeded=payment_intent.status == 'succeeded',
                    order=order,
                    user=user,
                    created_by=user,
                    last_updated_by=user,
                    last_update_login=user,
                )

                payment.save()

                order.payment_status = 'succeeded'
                order.save()

                notification = OrderNotifications.objects.create(
                    order=order,
                    status='pending'
                )
                notification.save()

                cart_items.delete()

            # Return response
            return Response({
                'message': 'Order Confirmed',
                'data': {
                    'order_details': OrderSerializer(order).data,
                    'order_items': OrderItemSerializer(order_items, many=True).data
                }
            }, status=status.HTTP_200_OK)

        except stripe.error.CardError as e:
            message = str(e)
            print(message)
            if ":" in message:
                message = message.split(": ")[1]
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)



# class CreatePayment(GenericAPIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     authentication_classes = [TokenAuthentication]
#     serializer_class = SelectPackageSerializer

#     def post(self, request):
#         payment = self.get_serializer(data=request.data)
#         if not payment.is_valid():
#             return Response(
#                 {'message': payment.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#                 )
#         payment = payment.data
#         package = Package.objects.get(name=payment["package_name"])
#         user = self.request.user
#         data = request.data
#         stripe.api_key = settings.STRIPE_SECRET_KEY

#         payment_method_id = data['payment_method_id']
#         customer_data = stripe.Customer.list(email=user.email).data

#         # if the array is empty it means the email has not been used yet
#         if len(customer_data) == 0:
#             # creating customer
#             customer = stripe.Customer.create(
#                 name=user.name,
#                 email=user.email,
#                 payment_method=payment_method_id
#                 )
#         else:
#             customer = customer_data[0]

#         try:
#             payment_intent = stripe.PaymentIntent.create(
#                 customer=customer,
#                 payment_method=payment_method_id,
#                 currency='usd',  # you can provide any currency you want
#                 amount=int((package.price * (1 + package.vat_percent)) * 100),
#                 confirm=True,
#                 return_url="http://localhost:9001/",
#                 receipt_email=user.email
#                 )
#             previous_payments = Payment.objects.filter(
#                 organization=user.organization
#                 )
#             for p_payment in previous_payments:
#                 p_payment.is_active = False
#                 p_payment.save()

#             payment = Payment(
#                 payment_intent_id=payment_intent.id,
#                 organization=user.organization,
#                 succeeded=payment_intent.status == 'succeeded',
#                 is_active=True,
#                 created_by=user.id,
#                 last_updated_by=user.id,
#                 last_update_login=user.id
#             )
#             payment.save()

#             order_num = payment.payment_intent_id.split('_')
#             order_no = order_num[1]

#             def format_date_in_words(date):
#                 day = date.day
#                 suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
#                 return date.strftime("%d{} %b, %y").format(suffix)

#             formatted_invoice_date = format_date_in_words(payment.creation_date)
#             vat_percent = package.vat_percent

#             vat = round(package.price * vat_percent, 2)
#             total = round(package.price * (1 + vat_percent), 2)
#             package_name = package.name.upper()

#             # send invoice to user email
#             subject = "SMMART - Payment Confirmation"
#             html_message = render_to_string(
#                 'payment/invoice.html',
#                 context={
#                     'username': user.name, 'package_price': package.price,
#                     'total': total, 'invoice_date': formatted_invoice_date,
#                     'order_no': order_no, 'package_name': package_name,
#                     'vat': vat,
#                     }
#             )
#             send_mail(
#                 subject,
#                 message=None,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 html_message=html_message
#             )

#             return Response(
#                 status=status.HTTP_200_OK,
#                 data={
#                     'message': 'Success',
#                     'data': {'customer_id': customer.email},
#                     'payment': {
#                         'id': payment.id,
#                         'organization': user.organization.name
#                     }
#                 }
#             )
#         except stripe.error.CardError as e:
#             message = str(e)
#             print(message)
#             if ":" in message:
#                 message = message.split(": ")[1]
#             return Response(
#                 {'message': message},
#                 status=status.HTTP_400_BAD_REQUEST
#                 )
