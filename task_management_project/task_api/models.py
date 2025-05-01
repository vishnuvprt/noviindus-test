from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
)

class Task(models.Model):
    title = models.CharField(max_length=200,null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='assigned_tasks',
        null=True,
        blank=True
    )
    assigned_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='created_tasks',
        null=True,
        blank=True
    )
    due_date = models.DateTimeField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()}) - {self.assigned_to.username}"
    
    def mark_completed(self, completion_report, worked_hours):
        """
        Mark a task as completed and record completion details.
        """
        self.status = 'completed'
        self.completion_report = completion_report
        self.worked_hours = worked_hours
        self.completed_at = timezone.now()
        self.save()
        
    def is_overdue(self):
        """
        Check if task is overdue.
        """
        if self.status != 'completed' and self.due_date < timezone.now():
            return True
        return False