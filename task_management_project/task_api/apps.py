from django.apps import AppConfig


class TaskApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_api'
    verbose_name = 'Task Management'
    
    def ready(self):
        import task_api.signals  # noqa