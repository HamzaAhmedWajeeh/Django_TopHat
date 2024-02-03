"""
Views for the User API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
# from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
# from django.conf import settings
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from core.models import User
# from user.utils import encrypt_email

from user.serializers import (
    # ForgetPasswordConfirmSerializer,
    # ForgetPasswordSerializer,
    UserSerializer,
    AuthTokenSerializer,
    UserUpdateSerializer,
    # ForgetPasswordSerializer,
    # ForgetPasswordConfirmSerializer
)
# from user.utils import encrypt_email
# from core.models import User

from django.contrib.auth import get_user_model


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user in the system

    Args:
        generics (_type_): _description_
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class CreateAdminUserView(generics.CreateAPIView):
    """
    Create a new admin user in the system

    Args:
        generics (_type_): _description_
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save(is_staff=True)
# class UserVerificationView(APIView):
#     def get(self, request, token):
#         user = User.get_user_by_verification_token(token)
#         if user and not user.verified:
#             user.verified = True
#             user.save()
#             subject = "Welcome To SMMART.ai"
#             html_message = render_to_string(
#                 'accounts/account_create_email.html'
#                 )
#             numnber_of_email = send_mail(
#                 subject,
#                 message=None,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 html_message=html_message
#                 )

#             print(f"{numnber_of_email} sent to user {user.email}!")
#             return Response(
#                 {'detail': 'User successfully verified'},
#                 status=status.HTTP_200_OK
#                 )
#         else:
#             return Response(
#                 {'detail': 'Invalid or already verified token'},
#                 status=status.HTTP_400_BAD_REQUEST
#                 )


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
            )
        user = serializer.validate(request.data)
        print(user)
        token, created = Token.objects.get_or_create(user=user)

        if not user.verified:
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'verified': user.verified,
            })
        else:
            return Response({
                'detail': _('User not verified.'),
            }, status=status.HTTP_401_UNAUTHORIZED)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authneticated user"""
        return self.request.user

    def get_serializer_class(self):
        # Use UserUpdateSerializer for PUT and PATCH requests
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


# class UserResetPassword(APIView):
#     serializer_class = ForgetPasswordSerializer
#     parmission_classes = [permissions.AllowAny]

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)

#         if serializer.is_valid():
#             email = serializer.validated_data.get('email')
#              # Example custom validation: Check if the email exists in the User model
#             if not User.objects.filter(email=email).exists():
#                 return Response({"errors": 'This email is not registered.'},
#                             status=status.HTTP_400_BAD_REQUEST)

#             token = encrypt_email(email=email,
#                                   key=settings.ENCRYPTION_KEY.encode('utf-8'))

#             password_reset_link = f"https://app.smmart.ai/#/resetPassword?token={token.decode()}"

#             subject = "Reset Password!"
#             html_message = render_to_string(
#                 'accounts/password_reset_email.html',
#                 context={'password_reset_link': password_reset_link})
#             number_of_email = send_mail(
#                 subject,
#                 message=None,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[email],
#                 html_message=html_message
#                 )
#             # Your password reset logic here...
#             return Response({"message": "Password reset request received."},
#                             status=status.HTTP_200_OK)
#         else:
#             return Response({"errors": serializer.errors},
#                             status=status.HTTP_400_BAD_REQUEST)


# class UserResetPasswordConfirm(APIView):
#     serializer_class = ForgetPasswordConfirmSerializer
#     parmission_classes = [permissions.AllowAny]

#     def post(self, request):
#         data = self.serializer_class().validate(data=request.data)
#         user = User.objects.get(email=data['email'])

#         user.set_password(data['password'])
#         user.save()

#         return Response({'message': "Password updated successfully!"},
#                         status=status.HTTP_201_CREATED)