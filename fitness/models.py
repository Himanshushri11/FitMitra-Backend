from django.db import models


class Goal(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class WorkoutDay(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    day_name = models.CharField(max_length=15)
    focus = models.CharField(max_length=100)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.day_name} - {self.focus}"


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    target_muscle = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DayExercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    section = models.CharField(max_length=20)  
    # warmup / main / finisher / cooldown

    sets = models.IntegerField()
    reps = models.CharField(max_length=20)
    rest_seconds = models.IntegerField()
    order = models.IntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.exercise.name} ({self.workout_day.day_name})"
