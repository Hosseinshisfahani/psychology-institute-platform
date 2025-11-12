from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PackagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.packages'
    verbose_name = _('پکیج‌ها')
    verbose_name_plural = _('پکیج‌ها')

    def ready(self):
        # Import signal handlers to ensure package course access is granted after purchase
        import app.packages.signals  # noqa: F401
