from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission class to allow access only to SuperAdmin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'superadmin'


class IsAdmin(permissions.BasePermission):
    """
    Permission class to allow access only to Admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsRegularUser(permissions.BasePermission):
    """
    Permission class to allow access only to regular users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'user'