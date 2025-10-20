from django.urls import path, include

app_name = 'appointments'

urlpatterns = [
    # API URLs
    path('api/', include('app.appointments.api_urls')),
]