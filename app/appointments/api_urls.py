from django.urls import path
from .api_views import (
    # Public views
    AppointmentTypeListAPIView, StaffListAPIView, RoomListAPIView,
    TimeSlotListAPIView, MyAppointmentListAPIView, MyAppointmentDetailAPIView,
    CreateAppointmentAPIView, cancel_appointment, AppointmentFeedbackCreateAPIView,
    get_available_slots,
    
    # Admin views
    AdminAppointmentListAPIView, AdminAppointmentDetailAPIView,
    confirm_appointment, reject_appointment, AdminStaffListAPIView,
    AdminStaffDetailAPIView, AdminRoomListAPIView, AdminRoomDetailAPIView,
    AdminAppointmentTypeListAPIView, AdminAppointmentTypeDetailAPIView,
    AdminTimeSlotListAPIView, AdminTimeSlotDetailAPIView
)

app_name = 'appointments'

urlpatterns = [
    # Public endpoints
    path('appointment-types/', AppointmentTypeListAPIView.as_view(), name='appointment_types'),
    path('staff/', StaffListAPIView.as_view(), name='staff_list'),
    path('rooms/', RoomListAPIView.as_view(), name='room_list'),
    path('time-slots/', TimeSlotListAPIView.as_view(), name='time_slots'),
    path('my-appointments/', MyAppointmentListAPIView.as_view(), name='my_appointments'),
    path('my-appointments/<int:pk>/', MyAppointmentDetailAPIView.as_view(), name='my_appointment_detail'),
    path('create/', CreateAppointmentAPIView.as_view(), name='create_appointment'),
    path('cancel/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('feedback/', AppointmentFeedbackCreateAPIView.as_view(), name='appointment_feedback'),
    path('available-slots/', get_available_slots, name='available_slots'),
    
    # Admin endpoints (to be included in admin panel)
    path('admin/appointments/', AdminAppointmentListAPIView.as_view(), name='admin_appointments'),
    path('admin/appointments/<int:pk>/', AdminAppointmentDetailAPIView.as_view(), name='admin_appointment_detail'),
    path('admin/appointments/<int:appointment_id>/confirm/', confirm_appointment, name='admin_confirm_appointment'),
    path('admin/appointments/<int:appointment_id>/reject/', reject_appointment, name='admin_reject_appointment'),
    path('admin/staff/', AdminStaffListAPIView.as_view(), name='admin_staff'),
    path('admin/staff/<int:pk>/', AdminStaffDetailAPIView.as_view(), name='admin_staff_detail'),
    path('admin/rooms/', AdminRoomListAPIView.as_view(), name='admin_rooms'),
    path('admin/rooms/<int:pk>/', AdminRoomDetailAPIView.as_view(), name='admin_room_detail'),
    path('admin/appointment-types/', AdminAppointmentTypeListAPIView.as_view(), name='admin_appointment_types'),
    path('admin/appointment-types/<int:pk>/', AdminAppointmentTypeDetailAPIView.as_view(), name='admin_appointment_type_detail'),
    path('admin/time-slots/', AdminTimeSlotListAPIView.as_view(), name='admin_time_slots'),
    path('admin/time-slots/<int:pk>/', AdminTimeSlotDetailAPIView.as_view(), name='admin_time_slot_detail'),
]