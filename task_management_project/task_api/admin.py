from django.contrib import admin
from django.utils.html import format_html
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'assigned_by', 'due_date', 'status_colored', 'worked_hours')
    list_filter = ('status', 'assigned_by', 'assigned_to')
    search_fields = ('title', 'description', 'assigned_to__username', 'assigned_by__username')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    autocomplete_fields = ['assigned_to', 'assigned_by']
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'assigned_to', 'assigned_by', 'due_date', 'status')
        }),
        ('Completion Details', {
            'fields': ('completion_report', 'worked_hours', 'completed_at'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def status_colored(self, obj):
        """
        Display task status with color coding.
        """
        colors = {
            'pending': 'orange',
            'in_progress': 'blue',
            'completed': 'green',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """
        Auto-assign the current admin user as the assignee when creating a task.
        """
        if not change:  # Only for new tasks
            if not obj.assigned_by_id:
                obj.assigned_by = request.user
        super().save_model(request, obj, form, change)