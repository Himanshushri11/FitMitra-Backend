from rest_framework.views import APIView
from rest_framework.response import Response
from .models import WorkoutDay
from .serializers import WorkoutDaySerializer


class WeeklyWorkoutAPIView(APIView):
    def get(self, request):
        goal_id = request.query_params.get("goal")
        days = WorkoutDay.objects.filter(
            goal_id=goal_id
        ).order_by("order")
        serializer = WorkoutDaySerializer(days, many=True)
        return Response(serializer.data)
