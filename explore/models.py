from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Gym(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0.0
    )
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.ImageField(upload_to='gym_thumbnails/', blank=True, null=True)
    facilities = models.JSONField(default=list, help_text="List of facilities like ['WiFi', 'Shower', 'Parking']")
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class GymImage(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gym_gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.gym.name}"

class GymReview(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='reviews')
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name}'s review for {self.gym.name}"

class Trainer(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, default="General Fitness")
    bio = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to='trainers/', blank=True, null=True)
    experience_years = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('completed', 'Completed'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to='events/banners/', blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name='events')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    participants_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title

class Challenge(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    banner = models.ImageField(upload_to='challenges/banners/', blank=True, null=True)
    duration_days = models.IntegerField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    start_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name='articles')
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    read_time_minutes = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

# User Participation Models
from django.conf import settings

class UserEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='joined_events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'event')

class UserChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='joined_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    progress_percentage = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'challenge')
