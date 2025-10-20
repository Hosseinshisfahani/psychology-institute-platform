from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    ClinicLocation, AppointmentType, TherapistSchedule, TherapistTimeOff,
    Appointment, AppointmentCancellation, AppointmentReschedule,
    CancellationPolicy, AppointmentReminder
)


@admin.register(ClinicLocation)
class ClinicLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'created_at']
    search_fields = ['name', 'address', 'city', 'phone']
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_duration_minutes', 'price', 'color_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'price']
    ordering = ['name']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'رنگ'


@admin.register(TherapistSchedule)
class TherapistScheduleAdmin(admin.ModelAdmin):
    list_display = ['therapist', 'day_of_week', 'start_time', 'end_time', 'location', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'location', 'therapist']
    search_fields = ['therapist__first_name', 'therapist__last_name', 'therapist__email']
    list_editable = ['is_active']
    ordering = ['therapist', 'day_of_week', 'start_time']


@admin.register(TherapistTimeOff)
class TherapistTimeOffAdmin(admin.ModelAdmin):
    list_display = ['therapist', 'start_date', 'end_date', 'reason', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'start_date', 'therapist']
    search_fields = ['therapist__first_name', 'therapist__last_name', 'reason']
    list_editable = ['is_approved']
    ordering = ['-start_date']


class AppointmentCancellationInline(admin.StackedInline):
    model = AppointmentCancellation
    extra = 0
    readonly_fields = ['cancelled_at']


class AppointmentRescheduleInline(admin.TabularInline):
    model = AppointmentReschedule
    fk_name = 'original_appointment'
    extra = 0
    readonly_fields = ['rescheduled_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client', 'therapist', 'appointment_type', 'scheduled_datetime', 
        'duration_minutes', 'status', 'location', 'created_at'
    ]
    list_filter = ['status', 'appointment_type', 'location', 'therapist', 'scheduled_datetime']
    search_fields = [
        'client__first_name', 'client__last_name', 'client__email',
        'therapist__first_name', 'therapist__last_name', 'therapist__email'
    ]
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AppointmentCancellationInline, AppointmentRescheduleInline]
    ordering = ['-scheduled_datetime']
    
    fieldsets = (
        (_('اطلاعات نوبت'), {
            'fields': ('client', 'therapist', 'appointment_type', 'location')
        }),
        (_('زمان‌بندی'), {
            'fields': ('scheduled_datetime', 'duration_minutes', 'status')
        }),
        (_('یادداشت‌ها'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client', 'therapist', 'appointment_type', 'location'
        )


@admin.register(AppointmentCancellation)
class AppointmentCancellationAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'cancelled_by', 'cancelled_at', 'cancellation_fee', 'refund_amount']
    list_filter = ['cancelled_at', 'appointment__therapist']
    search_fields = [
        'appointment__client__first_name', 'appointment__client__last_name',
        'appointment__therapist__first_name', 'appointment__therapist__last_name',
        'reason'
    ]
    readonly_fields = ['cancelled_at']
    ordering = ['-cancelled_at']


@admin.register(AppointmentReschedule)
class AppointmentRescheduleAdmin(admin.ModelAdmin):
    list_display = ['original_appointment', 'new_appointment', 'rescheduled_by', 'rescheduled_at', 'reschedule_fee']
    list_filter = ['rescheduled_at', 'original_appointment__therapist']
    search_fields = [
        'original_appointment__client__first_name', 'original_appointment__client__last_name',
        'reason'
    ]
    readonly_fields = ['rescheduled_at']
    ordering = ['-rescheduled_at']


@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'hours_before_appointment', 'cancellation_fee_percentage', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'cancellation_fee_percentage']
    ordering = ['-hours_before_appointment']


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'scheduled_time', 'status', 'sent_at']
    list_filter = ['reminder_type', 'status', 'scheduled_time']
    search_fields = [
        'appointment__client__first_name', 'appointment__client__last_name',
        'appointment__therapist__first_name', 'appointment__therapist__last_name'
    ]
    readonly_fields = ['sent_at', 'created_at']
    ordering = ['scheduled_time']
