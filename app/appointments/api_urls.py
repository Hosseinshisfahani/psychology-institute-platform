from django.urls import path
from .api_views import (
    # Appointment Types
    AppointmentTypeListAPIView,
    AppointmentTypeDetailAPIView,
    
    # Specialists
    SpecialistListAPIView,
    SpecialistDetailAPIView,
    
    # Time Slots
    TimeSlotListAPIView,
    
    # Appointments
    AppointmentListAPIView,
    AppointmentDetailAPIView,
    get_available_slots,
    confirm_appointment,
    cancel_appointment,
    mark_appointment_complete,
    
    # Waiting List
    WaitingListCreateAPIView,
    WaitingListListAPIView,
    remove_from_waiting_list,
    
    # Statistics
    appointment_statistics,
)

app_name = 'appointments'

urlpatterns = [
    # Appointment Types
    path('types/', AppointmentTypeListAPIView.as_view(), name='appointment_types'),
    path('types/<int:pk>/', AppointmentTypeDetailAPIView.as_view(), name='appointment_type_detail'),
    
    # Specialists
    path('specialists/', SpecialistListAPIView.as_view(), name='specialists'),
    path('specialists/<int:pk>/', SpecialistDetailAPIView.as_view(), name='specialist_detail'),
    
    # Time Slots
    path('time-slots/', TimeSlotListAPIView.as_view(), name='time_slots'),
    
    # Available Slots
    path('available-slots/', get_available_slots, name='available_slots'),
    
    # Appointments
    path('', AppointmentListAPIView.as_view(), name='appointments'),
    path('<int:pk>/', AppointmentDetailAPIView.as_view(), name='appointment_detail'),
    path('<int:appointment_id>/confirm/', confirm_appointment, name='confirm_appointment'),
    path('<int:appointment_id>/cancel/', cancel_appointment, name='cancel_appointment'),
    path('<int:appointment_id>/complete/', mark_appointment_complete, name='mark_appointment_complete'),
    
    # Waiting List
    path('waiting-list/add/', WaitingListCreateAPIView.as_view(), name='add_to_waiting_list'),
    path('waiting-list/', WaitingListListAPIView.as_view(), name='waiting_list'),
    path('waiting-list/<int:waiting_list_id>/remove/', remove_from_waiting_list, name='remove_from_waiting_list'),
    
    # Statistics
    path('statistics/', appointment_statistics, name='appointment_statistics'),
]