from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MmpiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.mmpi'
    verbose_name = _('MMPI')
    verbose_name_plural = _('MMPI')

