from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdminPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.admin_panel'
    verbose_name = _('مدیریت موسسه روانشناسی')
    verbose_name_plural = _('مدیریت موسسه روانشناسی')