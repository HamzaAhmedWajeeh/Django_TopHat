"""
Django Admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Adming pages for user"""
    ordering = ['id']
    list_display = ['email', 'name', 'address', 'city']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),

    )
    readonly_fields = ['id']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'package',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Categories)
admin.site.register(models.Feedback)
admin.site.register(models.MenuItems)
admin.site.register(models.ItemExtras)
admin.site.register(models.Extras)
admin.site.register(models.Payments)
admin.site.register(models.Orders)
admin.site.register(models.OrderItems)
admin.site.register(models.LoyaltyPoints)
admin.site.register(models.Cart)