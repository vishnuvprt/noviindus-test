from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_CHOICES = (
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )
class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    managed_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_users'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def is_superadmin(self):
        return self.role == 'superadmin'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_regular_user(self):
        return self.role == 'user'
    
    @property
    def name(self):
        return f"{self.first_name} ({self.last_name})"
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"