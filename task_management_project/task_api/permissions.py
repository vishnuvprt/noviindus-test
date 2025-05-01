from rest_framework import permissions


class IsTaskOwner(permissions.BasePermission):
    """
    Permission class to allow access only to users assigned to the task.
    """
    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user


class CanManageTask(permissions.BasePermission):
    """
    Permission to check if user can manage the task based on their role.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        # SuperAdmins can manage any task
        if user.role == 'superadmin':
            return True
        # Admins can manage tasks assigned to users they manage
        if user.role == 'admin':
            return obj.assigned_to.managed_by == user or obj.assigned_by == user
        # Task owners can only view their tasks
        return obj.assigned_to == user and request.method in permissions.SAFE_METHODS


class CanViewTaskReport(permissions.BasePermission):
    """
    Permission to check if user can view task reports.
    Only Admins and SuperAdmins can view task reports.
    """
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'superadmin']
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        # SuperAdmins can view any report
        if user.role == 'superadmin':
            return True
        # Admins can view reports for tasks assigned to users they manage
        if user.role == 'admin':
            return obj.assigned_to.managed_by == user or obj.assigned_by == user
        return False