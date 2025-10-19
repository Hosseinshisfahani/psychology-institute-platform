from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TherapySessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.therapy_sessions'
    verbose_name = _('جلسات درمانی')
    verbose_name_plural = _('جلسات درمانی')