from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.dashboard'
    verbose_name = _('داشبورد')
    verbose_name_plural = _('داشبورد')
