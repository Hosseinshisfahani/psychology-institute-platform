from django.urls import path
from .api_views import (
    StaffListAPIView, StaffDetailAPIView, AppointmentTypeListAPIView,
    AppointmentRoomListAPIView, MyAppointmentListAPIView, AppointmentDetailAPIView,
    CreateAppointmentAPIView, get_available_slots, cancel_appointment,
    reschedule_appointment, AppointmentFeedbackCreateAPIView, MyFeedbackListAPIView,
    appointment_statistics, StaffAppointmentListAPIView, confirm_appointment,
    complete_appointment
)

urlpatterns = [
    # Public endpoints
    path('staff/', StaffListAPIView.as_view(), name='api_staff_list'),
    path('staff/<int:pk>/', StaffDetailAPIView.as_view(), name='api_staff_detail'),
    path('appointment-types/', AppointmentTypeListAPIView.as_view(), name='api_appointment_types'),
    path('available-slots/', get_available_slots, name='api_available_slots'),
    
    # User appointments
    path('my-appointments/', MyAppointmentListAPIView.as_view(), name='api_my_appointments'),
    path('appointments/<int:pk>/', AppointmentDetailAPIView.as_view(), name='api_appointment_detail'),
    path('appointments/create/', CreateAppointmentAPIView.as_view(), name='api_create_appointment'),
    path('appointments/<int:appointment_id>/cancel/', cancel_appointment, name='api_cancel_appointment'),
    path('appointments/<int:appointment_id>/reschedule/', reschedule_appointment, name='api_reschedule_appointment'),
    
    # Feedback
    path('feedback/create/', AppointmentFeedbackCreateAPIView.as_view(), name='api_create_feedback'),
    path('my-feedback/', MyFeedbackListAPIView.as_view(), name='api_my_feedback'),
    
    # Statistics
    path('statistics/', appointment_statistics, name='api_appointment_statistics'),
    
    # Staff endpoints
    path('staff-appointments/', StaffAppointmentListAPIView.as_view(), name='api_staff_appointments'),
    path('appointments/<int:appointment_id>/confirm/', confirm_appointment, name='api_confirm_appointment'),
    path('appointments/<int:appointment_id>/complete/', complete_appointment, name='api_complete_appointment'),
    
    # Room management (staff only)
    path('rooms/', AppointmentRoomListAPIView.as_view(), name='api_appointment_rooms'),
]