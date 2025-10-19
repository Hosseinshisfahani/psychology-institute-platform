from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.reports'
    verbose_name = _('گزارش‌ها')
    verbose_name_plural = _('گزارش‌ها')
