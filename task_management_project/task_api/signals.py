from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task


@receiver(pre_save, sender=Task)
def handle_task_completion(sender, instance, **kwargs):
    """
    Signal to automatically set completed_at timestamp when a task is marked as completed.
    """
    try:
        # Get the original task object from the database
        old_task = Task.objects.get(pk=instance.pk)
        
        # Check if the task is being marked as completed
        if old_task.status != 'completed' and instance.status == 'completed':
            # Set the completed_at timestamp if not already set
            if not instance.completed_at:
                instance.completed_at = timezone.now()
                
    except Task.DoesNotExist:
        # This is a new task being created, no need to handle completion
        pass