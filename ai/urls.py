from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.AIChatAPIView.as_view(), name="chat_with_fitty"),
    path("posture-analysis/", views.PostureAnalysisAPIView.as_view(), name="posture_analysis"),
]
