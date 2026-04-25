# ==============================================================================
# Landing App — Application Configuration
# ==============================================================================
from django.apps import AppConfig


class LandingConfig(AppConfig):
    """Configuration for the CECP landing page application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'landing'
    verbose_name = 'CECP Landing Page'

    def ready(self):
        import landing.signals
