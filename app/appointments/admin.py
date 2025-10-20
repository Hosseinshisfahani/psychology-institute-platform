from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    AppointmentType, Specialist, TimeSlot, Appointment,
    AppointmentReminder, WaitingList
)
import jdatetime


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_minutes', 'price', 'requires_specialist', 'is_active']
    list_filter = ['is_active', 'requires_specialist']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialization', 'room_number', 'experience_years', 'is_available']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    raw_id_fields = ['user']
    ordering = ['user__first_name', 'user__last_name']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Full Name')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['get_specialist_name', 'day_of_week', 'start_time', 'end_time', 'max_appointments', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['specialist__user__first_name', 'specialist__user__last_name']
    raw_id_fields = ['specialist']
    ordering = ['day_of_week', 'start_time']
    
    def get_specialist_name(self, obj):
        return obj.specialist.user.get_full_name() if obj.specialist else "General"
    get_specialist_name.short_description = _('Specialist')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'appointment_number', 'get_client_name', 'appointment_type',
        'get_specialist_name', 'appointment_date', 'appointment_time',
        'status', 'is_paid'
    ]
    list_filter = ['status', 'is_paid', 'appointment_date', 'appointment_type']
    search_fields = [
        'appointment_number', 'client__first_name', 'client__last_name',
        'client__email', 'client_phone'
    ]
    raw_id_fields = ['client', 'specialist']
    readonly_fields = [
        'appointment_number', 'created_at', 'updated_at',
        'confirmed_at', 'completed_at', 'cancelled_at'
    ]
    date_hierarchy = 'appointment_date'
    ordering = ['-appointment_date', '-appointment_time']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('appointment_number', 'client', 'appointment_type', 'specialist', 'status')
        }),
        (_('Scheduling'), {
            'fields': ('appointment_date', 'appointment_time', 'duration_minutes', 'room_number')
        }),
        (_('Contact Information'), {
            'fields': ('client_phone', 'emergency_contact')
        }),
        (_('Details'), {
            'fields': ('reason_for_visit', 'notes')
        }),
        (_('Payment'), {
            'fields': ('price', 'is_paid', 'payment_method')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_client_name(self, obj):
        return obj.client.get_full_name()
    get_client_name.short_description = _('Client')
    
    def get_specialist_name(self, obj):
        return obj.specialist.user.get_full_name() if obj.specialist else "-"
    get_specialist_name.short_description = _('Specialist')
    
    def get_appointment_date_persian(self, obj):
        if obj.appointment_date:
            return jdatetime.date.fromgregorian(date=obj.appointment_date).strftime('%Y/%m/%d')
        return "-"
    get_appointment_date_persian.short_description = _('Appointment Date (Persian)')


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = [
        'get_appointment_number', 'reminder_type', 'scheduled_time',
        'is_sent', 'sent_at'
    ]
    list_filter = ['reminder_type', 'is_sent']
    search_fields = ['appointment__appointment_number']
    raw_id_fields = ['appointment']
    readonly_fields = ['sent_at', 'created_at']
    ordering = ['scheduled_time']
    
    def get_appointment_number(self, obj):
        return obj.appointment.appointment_number
    get_appointment_number.short_description = _('Appointment Number')


@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = [
        'get_client_name', 'appointment_type', 'get_specialist_name',
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'appointment_type']
    search_fields = ['client__first_name', 'client__last_name', 'client__email']
    raw_id_fields = ['client', 'specialist']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['created_at']
    
    def get_client_name(self, obj):
        return obj.client.get_full_name()
    get_client_name.short_description = _('Client')
    
    def get_specialist_name(self, obj):
        return obj.specialist.user.get_full_name() if obj.specialist else "-"
    get_specialist_name.short_description = _('Preferred Specialist')