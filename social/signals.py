"""
FitMitra Social Signals
Automatic actions triggered by model events
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_social_profile(sender, instance, created, **kwargs):
    """
    Automatically create social profile when user is created
    """
    if created:
        # Generate username from user's username or email
        base_username = instance.username if instance.username else instance.email.split('@')[0]
        username = base_username
        
        # Ensure username is unique
        counter = 1
        while UserProfile.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        UserProfile.objects.create(
            user=instance,
            username=username
        )


@receiver(post_save, sender=User)
def save_social_profile(sender, instance, **kwargs):
    """
    Save social profile when user is saved
    """
    if hasattr(instance, 'social_profile'):
        instance.social_profile.save()
