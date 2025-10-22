from django.urls import path
from .api_views import (
    AppointmentListAPIView, AppointmentDetailAPIView, reschedule_appointment,
    cancel_appointment, TherapistListAPIView, TherapistDetailAPIView, TherapistAvailabilityAPIView,
    AppointmentTypeListAPIView, ClinicLocationListAPIView,
    CancellationPolicyListAPIView, appointment_statistics, appointment_availability
)

urlpatterns = [
    # Appointments
    path('', AppointmentListAPIView.as_view(), name='api_appointment_list'),
    path('<int:pk>/', AppointmentDetailAPIView.as_view(), name='api_appointment_detail'),
    path('<int:appointment_id>/reschedule/', reschedule_appointment, name='api_appointment_reschedule'),
    path('<int:appointment_id>/cancel/', cancel_appointment, name='api_appointment_cancel'),
    path('availability/', appointment_availability, name='api_appointment_availability'),
    
    # Therapists
    path('therapists/', TherapistListAPIView.as_view(), name='api_therapist_list'),
    path('therapists/<int:therapist_id>/', TherapistDetailAPIView.as_view(), name='api_therapist_detail'),
    path('therapists/<int:therapist_id>/availability/', TherapistAvailabilityAPIView.as_view(), name='api_therapist_availability'),
    
    # Reference data
    path('types/', AppointmentTypeListAPIView.as_view(), name='api_appointment_types'),
    path('locations/', ClinicLocationListAPIView.as_view(), name='api_clinic_locations'),
    path('cancellation-policies/', CancellationPolicyListAPIView.as_view(), name='api_cancellation_policies'),
    
    # Statistics
    path('statistics/', appointment_statistics, name='api_appointment_statistics'),
]
