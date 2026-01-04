from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import GymViewSet

router = SimpleRouter()
router.register(r'gyms', GymViewSet, basename='gym')

urlpatterns = [
    path('', include(router.urls)),
]
