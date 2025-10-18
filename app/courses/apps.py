from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.courses'
    
    def ready(self):
        import app.courses.signals