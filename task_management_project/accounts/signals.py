from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def handle_user_role_change(sender, instance, created, **kwargs):
    """
    Signal to automatically adjust user permissions when role changes.
    """
    # If a user becomes a SuperAdmin, give them staff and superuser permissions
    if instance.role == 'superadmin':
        if not instance.is_staff or not instance.is_superuser:
            instance.is_staff = True
            instance.is_superuser = True
            instance.save(update_fields=['is_staff', 'is_superuser'])
    
    # If a user becomes an Admin, give them staff permissions
    elif instance.role == 'admin':
        if not instance.is_staff:
            instance.is_staff = True
            instance.is_superuser = False
            instance.save(update_fields=['is_staff', 'is_superuser'])
    
    # Regular users should not have staff or superuser permissions
    elif instance.role == 'user':
        if instance.is_staff or instance.is_superuser:
            instance.is_staff = False
            instance.is_superuser = False
            instance.save(update_fields=['is_staff', 'is_superuser'])