from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserAssignView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/assign-admin/', UserAssignView.as_view(), name='assign-admin'),
]