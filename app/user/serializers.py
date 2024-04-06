"""
Serializers for the User API view
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
    )
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from rest_framework import serializers
# from django.utils import timezone
from core.models import (
    User
    )

from user.utils import decrypt_email


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user Object"""

    class Meta:
        model = get_user_model()
        fields = [
            'email', 'password', 'name', 'address', 'city', 'state', 'post_code', 'phone'
            ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create and return a user with encrypted password"""

        user = get_user_model().objects.create_user(**validated_data)
        user.generate_verification_token()

        subject = "Verify Your Email"
        verification_link = f"http://localhost:4200/verification-stats?verification_token={user.verification_token}"
        html_message = render_to_string(
            'accounts/verify_email.html', {'verification_link': verification_link}
            )
        numnber_of_email = send_mail(
            subject,
            message=None,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message)
        return user

    def update(self, instance, validated_data) -> get_user_model():
        """Update and return user"""

        if 'email' in validated_data:
            raise serializers.ValidationError("Email cannot be changed.")

        password = validated_data.pop('password', None)
        user = super().update(instance=instance, validated_data=validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['password', 'name', 'address', 'city', 'state', 'post_code', 'phone']
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance=instance, validated_data=validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user Auth Token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        '''validate and authenticate user'''
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials!")
            raise serializers.ValidationError(msg, code='authorization')
        return user


class AdminAuthTokenSerializer(serializers.Serializer):
    """Serializer for the user Auth Token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        '''validate and authenticate admin user'''
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if user and not user.is_staff:
            msg = _("Only Admin Users Allowed.")
            raise serializers.ValidationError(msg, code='authorization')
        elif not user:
            msg = _("Unable to authenticate with provided credentials!")
            raise serializers.ValidationError(msg, code='authorization')
        return user


class ForgetPasswordSerializer(serializers.Serializer):
    """Serializer for the user Auth Token"""
    email = serializers.EmailField()


class ForgetPasswordConfirmSerializer(serializers.Serializer):
    """Serializer for the user Auth Token"""
    token = serializers.CharField(max_length=500)
    password = serializers.CharField(
        style={"input_type": 'password'},
        trim_whitespace=False
    )
    def validate(self, data):
        email = decrypt_email(encrypted_email=data['token'],
                              key=settings.ENCRYPTION_KEY.encode('utf-8'))
        if not email:
            raise serializers.ValidationError('The token has expired.')
        data['email'] = email
        return data
