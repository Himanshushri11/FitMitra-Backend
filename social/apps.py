from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social'
    verbose_name = 'Social & Community'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import social.signals  # noqa
        except ImportError:
            pass
