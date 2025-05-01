from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from task_api.models import Task
from task_api.serializers import TaskSerializer, TaskCompletionSerializer, TaskReportSerializer
from task_api.permissions import IsTaskOwner, CanViewTaskReport
from accounts.permissions import IsSuperAdmin, IsAdmin


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_superadmin():
            # SuperAdmins can see all tasks
            return Task.objects.select_related('assigned_to','assigned_by').all()
        elif user.is_admin():
            # Admins can see tasks assigned to users they manage
            return Task.objects.select_related('assigned_to','assigned_by').filter(
                Q(assigned_to__managed_by=user) | Q(assigned_by=user) | Q(assigned_to=user)
            )
        else:
            # Regular users can only see their own tasks
            return Task.objects.select_related('assigned_to','assigned_by').filter(assigned_to=user)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsSuperAdmin|IsAdmin]
        elif self.action == 'mark_completed':
            self.permission_classes = [IsAuthenticated, IsTaskOwner]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        user = request.user

        # Ensure only superadmin/admin reach here due to permissions
        data = request.data.copy()
        data['assigned_by'] = user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'], url_path='complete')
    def mark_completed(self, request, pk=None):
        task = self.get_object()
        
        if task.status == 'completed':
            return Response(
                {"detail": "Task is already marked as completed."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = TaskCompletionSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='report')
    def get_report(self, request, pk=None):
        task = self.get_object()  
        # Check if the task is completed
        if task.status != 'completed':
            return Response(
                {"detail": "Task is not completed yet."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check permissions
        self.check_object_permissions(request, task)
        
        serializer = TaskReportSerializer(task)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.action == 'mark_completed':
            return TaskCompletionSerializer
        elif self.action == 'get_report':
            return TaskReportSerializer
        return TaskSerializer


class UserTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.select_related('assigned_to').filter(assigned_to=self.request.user)