from django.apps import AppConfig


class PsychologyInstituteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'psychology_institute'

    def ready(self):
        from .admin_customization import unregister_third_party_models
        unregister_third_party_models()