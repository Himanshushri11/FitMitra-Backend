from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .services.gemini import get_gemini_response, get_posture_feedback

class AIChatAPIView(APIView):
    # TEMPORARY: AllowAny for testing (change back to IsAuthenticated later)
    permission_classes = [AllowAny]

    def post(self, request):
        message = request.data.get("message")
        
        # Get user goal from profile (handle both authenticated and anonymous)
        user_goal = "general fitness"
        try:
            if request.user and request.user.is_authenticated:
                user_goal = request.user.profile.goal if hasattr(request.user, 'profile') and request.user.profile.goal else "general fitness"
        except:
            user_goal = "general fitness"

        if not message:
            return Response({"error": "Message required"}, status=400)

        context = request.data.get("context", {})

        try:
            reply = get_gemini_response(message, user_goal, context=context)
            return Response({
                "type": "ai",
                "reply": reply
            })
        except Exception as e:
            return Response({
                "error": f"AI service error: {str(e)}"
            }, status=500)

class PostureAnalysisAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        workout = request.data.get("workout")
        exercise = request.data.get("exercise")
        posture_status = request.data.get("posture_status")
        issue = request.data.get("issue")
        device = request.data.get("device", "desktop")

        if not workout or not exercise or not posture_status:
            return Response({"error": "Missing posture data"}, status=400)

        try:
            # Get trainer-style feedback from Gemini
            feedback = get_posture_feedback(workout, exercise, posture_status, issue)
            
            return Response({
                "device": device,
                "workout": workout,
                "exercise": exercise,
                "posture_status": posture_status,
                "issue": issue,
                "feedback": feedback
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
