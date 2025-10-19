from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.blog'
    verbose_name = _('وبلاگ')
    verbose_name_plural = _('وبلاگ')
