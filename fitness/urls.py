from django.urls import path
from .views import WeeklyWorkoutAPIView

urlpatterns = [
    path("weekly/", WeeklyWorkoutAPIView.as_view()),
]
