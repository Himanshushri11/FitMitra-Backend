from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GymViewSet, ExploreDashboardView, EventViewSet, ChallengeViewSet, ArticleViewSet, TrainerViewSet

router = DefaultRouter()
router.register(r'gyms', GymViewSet, basename='gym')
router.register(r'events', EventViewSet, basename='event')
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'trainers', TrainerViewSet, basename='trainer')

urlpatterns = [
    path('dashboard/', ExploreDashboardView.as_view(), name='explore-dashboard'),
    path('', include(router.urls)),
]
