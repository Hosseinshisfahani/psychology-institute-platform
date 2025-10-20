from django.urls import path, include

app_name = 'appointments'

urlpatterns = [
    path('api/', include('app.appointments.api_urls')),
]