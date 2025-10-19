from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CohortsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.cohorts'
    verbose_name = _('دوره‌ها')
    verbose_name_plural = _('دوره‌ها')
