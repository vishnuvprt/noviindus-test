from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, UserTaskListView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('my-tasks/', UserTaskListView.as_view(), name='my-tasks'),
]