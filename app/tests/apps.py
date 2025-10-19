from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.tests'
    verbose_name = _('تست‌ها')
    verbose_name_plural = _('تست‌ها')
