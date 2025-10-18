from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.courses'
    verbose_name = 'بسته‌های آموزشی'
    
    def ready(self):
        import app.courses.signals