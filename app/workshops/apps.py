from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkshopsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.workshops'
    verbose_name = _('کارگاه‌ها')
    verbose_name_plural = _('کارگاه‌ها')
