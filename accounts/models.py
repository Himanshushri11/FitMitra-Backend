from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Info
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    height = models.FloatField(null=True, blank=True) # in cm
    weight = models.FloatField(null=True, blank=True) # in kg
    
    # Fitness Info
    goal = models.CharField(max_length=50, blank=True)
    fitness_level = models.CharField(max_length=50, blank=True)
    
    # Gamification / Stats
    workouts_completed = models.IntegerField(default=0)
    calories_burned = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    achievements_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Profile"
