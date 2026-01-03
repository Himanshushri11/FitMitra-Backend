from rest_framework import serializers
from .models import WorkoutDay, DayExercise


class DayExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source="exercise.name")

    class Meta:
        model = DayExercise
        fields = [
            "exercise_name",
            "section",
            "sets",
            "reps",
            "rest_seconds",
        ]


class WorkoutDaySerializer(serializers.ModelSerializer):
    exercises = DayExerciseSerializer(
        source="dayexercise_set", many=True
    )

    class Meta:
        model = WorkoutDay
        fields = ["day_name", "focus", "exercises"]
