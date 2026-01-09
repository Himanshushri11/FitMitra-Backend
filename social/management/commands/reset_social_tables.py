"""
Management command to reset social app tables
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Reset social app tables to fix migration issues'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('Dropping old social tables...')
            
            # Drop tables in correct order (respecting foreign keys)
            tables = [
                'social_block',
                'social_report',
                'social_notification',
                'social_message',
                'social_like',
                'social_comment',
                'social_post',
                'social_follow',
                'social_user_profile',
            ]
            
            for table in tables:
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
                    self.stdout.write(f'  Dropped {table}')
                except Exception as e:
                    self.stdout.write(f'  Warning: {table} - {str(e)}')
            
            # Delete migration record
            cursor.execute("DELETE FROM django_migrations WHERE app = 'social';")
            
            self.stdout.write(self.style.SUCCESS('Successfully reset social tables!'))
            self.stdout.write('Now run: python manage.py migrate social')
