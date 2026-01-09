"""
FitMitra Social URLs
API endpoints for social features
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Feed URLs
    path('feed/', views.feed_view, name='feed'),
    path('explore/', views.explore_feed_view, name='explore-feed'),
    
    # Follow URLs
    path('follow/', views.follow_user, name='follow'),
    path('unfollow/', views.unfollow_user, name='unfollow'),
    
    # Moderation URLs
    path('report/', views.report_content, name='report'),
    path('block/', views.block_user, name='block'),
    path('unblock/', views.unblock_user, name='unblock'),
]
