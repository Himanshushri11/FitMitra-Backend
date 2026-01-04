from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    AdminDashboardStatsView, 
    AdminUserViewSet, 
    AdminGymViewSet, 
    AdminActionListView
)

router = SimpleRouter()
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'gyms', AdminGymViewSet, basename='admin-gyms')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', AdminDashboardStatsView.as_view(), name='admin-stats'),
    path('logs/', AdminActionListView.as_view(), name='admin-logs'),
]
