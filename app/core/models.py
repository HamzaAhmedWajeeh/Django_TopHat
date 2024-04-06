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
    name = models.CharField(max_length=255,null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    post_code = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
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


class Categories(models.Model):
    name = models.CharField(max_length=255, null=True)
    # Who Columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Feedback(models.Model):
    user = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.CASCADE
        )
    message = models.CharField(max_length=450, null=True, blank=True)
    # Who Columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.name


class MenuItems(models.Model):
    name = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=500, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    large_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    medium_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    small_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(
        'Categories', null=True, blank=True, on_delete=models.CASCADE
        )
    image = models.ImageField(null=True, blank=True)
    image1 = models.ImageField(null=True, blank=True)
    image2 = models.ImageField(null=True, blank=True)
    image3 = models.ImageField(null=True, blank=True)
    image4 = models.ImageField(null=True, blank=True)
    image5 = models.ImageField(null=True, blank=True)
    # who columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class ItemExtras(models.Model):
    extras = models.ForeignKey(
        'Extras', null=True, blank=True, on_delete=models.CASCADE
        )

    # who columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)


class KitchenNotes(models.Model):
    menu_item = models.ForeignKey(
        'MenuItems', null=True, blank=True, on_delete=models.CASCADE
        )
    name = models.CharField(max_length=300, null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # who columns
    creation_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)


class Extras(models.Model):
    menu_item = models.ForeignKey(
        'MenuItems', null=True, blank=True, on_delete=models.CASCADE
        )
    name = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    # who columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)


class Payments(models.Model):
    order = models.ForeignKey(
        'Orders', null=True, blank=True, on_delete=models.CASCADE
        )
    user = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.CASCADE
        )
    succeeded = models.BooleanField(default=False)
    paid_by_points = models.BooleanField(default=False)
    payment_intent_id = models.CharField(max_length=500, null=True, blank=True)

    # who columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)


class Orders(models.Model):
    user = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.CASCADE
        )
    order_date = models.DateField(null=True, blank=True)
    order_time = models.TimeField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    order_status = models.CharField(max_length=30, null=True, blank=True)
    payment_status = models.CharField(max_length=30, null=True, blank=True)


class Sizes(models.Model):
    menu_item = models.ForeignKey(
        'MenuItems', null=True, blank=True, on_delete=models.CASCADE
        )
    large = models.BooleanField(default=False, null=True, blank=True)
    medium = models.BooleanField(default=False, null=True, blank=True)
    small = models.BooleanField(default=False, null=True, blank=True)
    # who columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)


class OrderItems(models.Model):
    order = models.ForeignKey(
        'Orders', null=True, blank=True, on_delete=models.CASCADE
        )
    item = models.ForeignKey(
        'MenuItems', null=True, blank=True, on_delete=models.CASCADE
        )
    size = models.CharField(max_length=7, null=True, blank=True)
    extras = models.CharField(max_length=255, null=True)
    kitchen_notes = models.CharField(max_length=255, null=True)
    quantity = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)


class OrderNotifications(models.Model):
    order = models.ForeignKey(
        'Orders', null=True, blank=True, on_delete=models.CASCADE
        )
    status = models.CharField(max_length=255, null=True, blank=True)
    # who columns
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(auto_now=True)
    last_updated_by = models.IntegerField(null=True, blank=True)
    last_update_login = models.IntegerField(null=True, blank=True)


class LoyaltyPoints(models.Model):
    user = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.CASCADE
        )
    points = models.DecimalField(max_digits=37, decimal_places=2, null=True, blank=True)


class Cart(models.Model):
    user = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.CASCADE
        )
    item = models.ForeignKey(
        'MenuItems', null=True, blank=True, on_delete=models.CASCADE
        )
    quantity = models.IntegerField(null=True, blank=True)
    size = models.CharField(max_length=7, null=True, blank=True)
    extras = models.CharField(max_length=255, null=True, blank=True)
    kitchen_notes = models.CharField(max_length=255, null=True, blank=True)
    total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
