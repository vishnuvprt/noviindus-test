from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserListSerializer
from .permissions import IsSuperAdmin, IsAdmin


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin():
            # SuperAdmins can see all users
            return User.objects.select_related('managed_by').all().exclude(is_superuser = True).order_by('-id')
        elif user.is_admin():
            # Admins can only see their managed users
            return User.objects.select_related('managed_by').filter(managed_by=user).order_by('-id')
        return User.objects.none()
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        # Only SuperAdmin can create admins
        if data.get('role') == 'admin' and not request.user.is_superadmin():
            return Response(
                {"detail": "You don't have permission to create admin users."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Only SuperAdmin can create SuperAdmins
        if data.get('role') == 'superadmin' and not request.user.is_superadmin():
            return Response(
                {"detail": "You don't have permission to create superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Set managed_by for users created by admins
        if request.user.is_admin() and not data.get('managed_by'):
            data['managed_by'] = request.user.id
            
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        
        # Check role change permissions
        if 'role' in data:
            # Only SuperAdmin can change roles
            if data['role'] != instance.role and not request.user.is_superadmin():
                return Response(
                    {"detail": "You don't have permission to change user roles."},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Only SuperAdmin can create/modify other SuperAdmins
            if data['role'] == 'superadmin' and not request.user.is_superadmin():
                return Response(
                    {"detail": "You don't have permission to assign superadmin role."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only SuperAdmin can delete SuperAdmins
        if instance.is_superadmin() and not request.user.is_superadmin():
            return Response(
                {"detail": "You don't have permission to delete superadmin users."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Only SuperAdmin can delete Admins
        if instance.is_admin() and not request.user.is_superadmin():
            return Response(
                {"detail": "You don't have permission to delete admin users."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        return super().destroy(request, *args, **kwargs)


class UserAssignView(generics.UpdateAPIView):
    #View for SuperAdmins to assign users to admins.
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = User.objects.all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        admin_id = request.data.get('managed_by')
        
        if not admin_id:
            return Response(
                {"detail": "Admin ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            admin = User.objects.get(id=admin_id, role='admin')
        except User.DoesNotExist:
            return Response(
                {"detail": "Admin not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        instance.managed_by = admin
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)