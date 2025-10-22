from django.urls import path
from . import views
from . import test_views

app_name = 'workshops'

urlpatterns = [
    # Add template-based views here if needed
    path('test-persian-calendar/', test_views.test_persian_calendar, name='test_persian_calendar'),
]

