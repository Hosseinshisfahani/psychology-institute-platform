from django.contrib import admin
from .models import (
    Staff, Room, AppointmentType, TimeSlot, Appointment,
    AppointmentCancellation, AppointmentReminder, AppointmentFeedback
)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'title', 'is_available', 'can_accept_appointments', 'office_location']
    list_filter = ['role', 'is_available', 'can_accept_appointments']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'title']
    raw_id_fields = ['user']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'floor', 'capacity', 'is_available']
    list_filter = ['building', 'floor', 'is_available']
    search_fields = ['name', 'building', 'facilities']


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_minutes', 'requires_approval', 'is_active']
    list_filter = ['requires_approval', 'is_active']
    search_fields = ['name', 'description']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['staff', 'day_of_week', 'start_time', 'end_time', 'is_available', 'max_appointments']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    raw_id_fields = ['staff']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'appointment_type', 'staff', 'appointment_date', 'appointment_time', 'status', 'room']
    list_filter = ['status', 'appointment_type', 'appointment_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'purpose']
    raw_id_fields = ['user', 'staff', 'confirmed_by']
    date_hierarchy = 'appointment_date'
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'completed_at']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'appointment_type', 'staff', 'room', 'status')
        }),
        ('زمانبندی', {
            'fields': ('appointment_date', 'appointment_time', 'duration_minutes')
        }),
        ('جزئیات', {
            'fields': ('purpose', 'notes', 'internal_notes')
        }),
        ('تأیید', {
            'fields': ('confirmed_by', 'confirmed_at', 'confirmation_notes')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        })
    )


@admin.register(AppointmentCancellation)
class AppointmentCancellationAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'cancelled_by', 'cancelled_at']
    list_filter = ['cancelled_at']
    search_fields = ['appointment__user__first_name', 'appointment__user__last_name', 'reason']
    raw_id_fields = ['appointment', 'cancelled_by']


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'scheduled_time', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent']
    raw_id_fields = ['appointment']


@admin.register(AppointmentFeedback)
class AppointmentFeedbackAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'overall_rating', 'would_recommend', 'created_at']
    list_filter = ['overall_rating', 'would_recommend']
    search_fields = ['appointment__user__first_name', 'appointment__user__last_name', 'comments']
    raw_id_fields = ['appointment']