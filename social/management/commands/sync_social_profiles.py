"""
Management command to create missing UserProfile records for existing users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from social.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create missing UserProfile records for existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                # Username generation logic similar to signals
                base_username = user.username if user.username else user.email.split('@')[0]
                username = base_username
                
                counter = 1
                while UserProfile.objects.filter(username=username).exclude(id=profile.id).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                profile.username = username
                profile.save()
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} missing UserProfiles!'))
