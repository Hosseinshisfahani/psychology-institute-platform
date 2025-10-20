from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Staff, AppointmentRoom, AppointmentType, StaffAvailability,
    TimeSlot, Appointment, AppointmentCancellation, AppointmentReminder,
    AppointmentFeedback
)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'role', 'title', 'room_number', 'is_available', 'accepts_appointments']
    list_filter = ['role', 'is_available', 'accepts_appointments', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'title', 'specializations']
    readonly_fields = ['created_at']
    fieldsets = (
        (_('اطلاعات کاربری'), {
            'fields': ('user',)
        }),
        (_('اطلاعات شغلی'), {
            'fields': ('role', 'title', 'specializations', 'room_number', 'phone_extension')
        }),
        (_('وضعیت'), {
            'fields': ('is_available', 'accepts_appointments')
        }),
        (_('اطلاعات تکمیلی'), {
            'fields': ('bio', 'profile_image')
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('نام کامل')


@admin.register(AppointmentRoom)
class AppointmentRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_number', 'floor', 'capacity', 'is_available']
    list_filter = ['floor', 'is_available', 'created_at']
    search_fields = ['name', 'room_number', 'facilities']
    readonly_fields = ['created_at']


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_minutes', 'price', 'is_active', 'max_advance_booking_days']
    list_filter = ['is_active', 'requires_preparation', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    fieldsets = (
        (_('اطلاعات پایه'), {
            'fields': ('name', 'description', 'duration_minutes', 'price')
        }),
        (_('تنظیمات رزرو'), {
            'fields': ('max_advance_booking_days', 'min_advance_booking_hours')
        }),
        (_('آمادگی'), {
            'fields': ('requires_preparation', 'preparation_instructions')
        }),
        (_('وضعیت'), {
            'fields': ('is_active', 'created_at')
        }),
    )


@admin.register(StaffAvailability)
class StaffAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['staff', 'get_day_display', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available', 'staff']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    filter_horizontal = ['appointment_types']
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = _('روز هفته')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'start_time', 'end_time', 'is_available', 'is_booked', 'appointment_type']
    list_filter = ['date', 'is_available', 'is_booked', 'staff', 'appointment_type']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'staff_name', 'appointment_type', 'date', 'start_time', 'status', 'is_paid']
    list_filter = ['status', 'date', 'is_paid', 'appointment_type', 'staff']
    search_fields = ['client__first_name', 'client__last_name', 'client__email', 
                     'staff__user__first_name', 'staff__user__last_name', 'phone_number']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'completed_at']
    fieldsets = (
        (_('اطلاعات اصلی'), {
            'fields': ('client', 'staff', 'appointment_type', 'status')
        }),
        (_('زمان‌بندی'), {
            'fields': ('date', 'start_time', 'end_time', 'time_slot', 'room')
        }),
        (_('جزئیات ملاقات'), {
            'fields': ('purpose', 'notes', 'internal_notes')
        }),
        (_('اطلاعات تماس'), {
            'fields': ('phone_number', 'alternative_phone')
        }),
        (_('پرداخت'), {
            'fields': ('price', 'is_paid', 'payment_method', 'transaction_id')
        }),
        (_('تایید و تکمیل'), {
            'fields': ('confirmed_at', 'confirmed_by', 'completed_at', 'arrival_time', 'departure_time')
        }),
        (_('تاریخ‌ها'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def client_name(self, obj):
        return obj.client.get_full_name()
    client_name.short_description = _('مراجع')
    
    def staff_name(self, obj):
        return obj.staff.get_full_name()
    staff_name.short_description = _('کارمند')
    
    actions = ['confirm_appointments', 'cancel_appointments', 'mark_as_completed']
    
    def confirm_appointments(self, request, queryset):
        count = 0
        for appointment in queryset.filter(status='pending'):
            appointment.confirm(request.user)
            count += 1
        self.message_user(request, f'{count} وقت ملاقات تایید شد.')
    confirm_appointments.short_description = _('تایید وقت‌های انتخاب شده')
    
    def cancel_appointments(self, request, queryset):
        count = queryset.filter(status__in=['pending', 'confirmed']).update(status='cancelled')
        self.message_user(request, f'{count} وقت ملاقات لغو شد.')
    cancel_appointments.short_description = _('لغو وقت‌های انتخاب شده')
    
    def mark_as_completed(self, request, queryset):
        count = 0
        for appointment in queryset.filter(status='confirmed'):
            appointment.complete()
            count += 1
        self.message_user(request, f'{count} وقت ملاقات به عنوان انجام شده علامت‌گذاری شد.')
    mark_as_completed.short_description = _('علامت‌گذاری به عنوان انجام شده')


@admin.register(AppointmentCancellation)
class AppointmentCancellationAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'cancelled_by_name', 'reason', 'cancelled_at', 'refund_amount', 'is_refunded']
    list_filter = ['reason', 'is_refunded', 'cancelled_at']
    search_fields = ['appointment__client__first_name', 'appointment__client__last_name',
                     'cancelled_by__first_name', 'cancelled_by__last_name', 'explanation']
    readonly_fields = ['cancelled_at']
    date_hierarchy = 'cancelled_at'
    
    def cancelled_by_name(self, obj):
        return obj.cancelled_by.get_full_name()
    cancelled_by_name.short_description = _('لغو شده توسط')


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'scheduled_time', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'scheduled_time']
    search_fields = ['appointment__client__first_name', 'appointment__client__last_name']
    readonly_fields = ['created_at', 'sent_at']
    date_hierarchy = 'scheduled_time'


@admin.register(AppointmentFeedback)
class AppointmentFeedbackAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'overall_rating', 'staff_rating', 'facility_rating', 'would_recommend', 'created_at']
    list_filter = ['overall_rating', 'would_recommend', 'created_at']
    search_fields = ['appointment__client__first_name', 'appointment__client__last_name', 'comments']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        (_('ملاقات'), {
            'fields': ('appointment',)
        }),
        (_('امتیازات'), {
            'fields': ('overall_rating', 'staff_rating', 'facility_rating', 'waiting_time_rating')
        }),
        (_('بازخورد'), {
            'fields': ('comments', 'would_recommend')
        }),
        (_('تاریخ'), {
            'fields': ('created_at',)
        }),
    )