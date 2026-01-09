from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, GymOwnerSignupView, LoginView, ProfileDetailView, ProfilePictureUploadView

urlpatterns = [
    path("signup/", SignupView.as_view()), # keep for backward compatibility
    path("signup/user/", SignupView.as_view()),
    path("signup/gym-owner/", GymOwnerSignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path("profile/", ProfileDetailView.as_view()),
    path("profile/upload-pic/", ProfilePictureUploadView.as_view()),
]
