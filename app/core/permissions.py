from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff == True)

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the feedback or an admin
        return obj.user == request.user or request.user.is_staff