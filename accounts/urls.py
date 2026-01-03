from django.urls import path
from .views import SignupView, LoginView, ProfileDetailView, ProfilePictureUploadView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("profile/", ProfileDetailView.as_view()),
    path("profile/upload-pic/", ProfilePictureUploadView.as_view()),
]
