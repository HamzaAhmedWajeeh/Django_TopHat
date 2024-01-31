from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.conf import settings
import hashlib


class UserManager(BaseUserManager):
    """MANAGER for User"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user"""

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and return new superuser"""

        user = self.create_user(email=email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """USER in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255,null=True)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    post_code = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def generate_verification_token(self):
        data_to_hash = f"{self.email}{settings.SECRET_KEY}"
        self.verification_token = hashlib.sha256(
            data_to_hash.encode()
            ).hexdigest()
        self.save()

    @staticmethod
    def get_user_by_verification_token(verification_token):
        try:
            return User.objects.get(verification_token=verification_token)
        except User.DoesNotExist:
            return None


# class Payment(models.Model):
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
#     succeeded = models.BooleanField(default=False)
#     payment_intent_id = models.CharField(max_length=500)
#     is_active = models.BooleanField(default=False)
#     is_subscription = models.BooleanField(default=False)

#     # who columns
#     creation_date = models.DateTimeField(auto_now=True)
#     created_by = models.IntegerField(null=True, blank=True)
#     last_update_date = models.DateTimeField(auto_now_add=True)
#     last_updated_by = models.IntegerField(null=True, blank=True)
#     last_update_login = models.IntegerField(null=True)

#     def __repr__(self) -> str:
#         active = "Active" if self.is_active else "InActive"
#         return f"{active} Payment by {self.organization.name}"

#     def __str__(self):
#         active = "Active" if self.is_active else "InActive"
#         return f"{active} Payment by {self.organization.name}"


#     @receiver(post_save, sender=Organization)
#     def create_payment(sender, instance, created, **kwargs):
#         if created:
#             Payment.objects.create(organization=instance)
