from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Therapist, SessionType, TherapistAvailability, Session, SessionNote,
    SessionRating, SessionCancellation, SessionReminder, SessionBooking
)


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'is_available', 'hourly_rate', 'created_at']
    list_filter = ['specialization', 'is_available', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'bio']
    readonly_fields = ['created_at']
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'is_available')
        }),
        ('تخصص و تجربه', {
            'fields': ('specialization', 'experience_start_date', 'hourly_rate')
        }),
        ('اطلاعات شخصی', {
            'fields': ('bio', 'education', 'certifications', 'profile_image')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class TherapistAvailabilityInline(admin.TabularInline):
    model = TherapistAvailability
    extra = 0
    fields = ['day_of_week', 'start_time', 'end_time', 'is_available']


@admin.register(SessionType)
class SessionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_minutes', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    fieldsets = (
        ('اطلاعات نوع جلسه', {
            'fields': ('name', 'description', 'duration_minutes', 'price', 'is_active')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class SessionNoteInline(admin.TabularInline):
    model = SessionNote
    extra = 0
    fields = ['note_type', 'content', 'is_private', 'created_by', 'created_at']
    readonly_fields = ['created_by', 'created_at']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['client', 'therapist', 'session_type', 'status', 'scheduled_date', 'scheduled_time', 'is_paid']
    list_filter = ['status', 'mode', 'is_paid', 'scheduled_date', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'therapist__user__first_name', 'therapist__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SessionNoteInline]
    fieldsets = (
        ('اطلاعات کلی', {
            'fields': ('client', 'therapist', 'session_type', 'status', 'mode')
        }),
        ('زمان‌بندی', {
            'fields': ('scheduled_date', 'scheduled_time', 'duration_minutes', 'started_at', 'ended_at')
        }),
        ('جزئیات جلسه', {
            'fields': ('location', 'meeting_link', 'meeting_id', 'meeting_password', 'goals', 'session_notes', 'homework')
        }),
        ('پرداخت', {
            'fields': ('price', 'is_paid', 'payment_method', 'transaction_id')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessionBooking)
class SessionBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'therapist', 'session_type', 'status', 'preferred_date', 'preferred_time', 'is_expired']
    list_filter = ['status', 'mode', 'preferred_date', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'therapist__user__first_name', 'therapist__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'is_expired']
    fieldsets = (
        ('اطلاعات کلی', {
            'fields': ('user', 'therapist', 'session_type', 'status', 'mode')
        }),
        ('زمان‌بندی درخواستی', {
            'fields': ('preferred_date', 'preferred_time', 'alternative_dates')
        }),
        ('جزئیات درخواست', {
            'fields': ('goals', 'notes', 'location', 'price')
        }),
        ('تایید نهایی', {
            'fields': ('confirmed_date', 'confirmed_time', 'confirmation_notes', 'confirmed_by', 'confirmed_at')
        }),
        ('اطلاعات Croom', {
            'fields': ('croom_class_id', 'croom_class_url', 'croom_meeting_id', 'croom_password'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'منقضی شده'


@admin.register(SessionNote)
class SessionNoteAdmin(admin.ModelAdmin):
    list_display = ['session', 'note_type', 'is_private', 'created_by', 'created_at']
    list_filter = ['note_type', 'is_private', 'created_at']
    search_fields = ['content', 'session__client__first_name', 'session__client__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('اطلاعات یادداشت', {
            'fields': ('session', 'note_type', 'content', 'is_private', 'created_by')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessionRating)
class SessionRatingAdmin(admin.ModelAdmin):
    list_display = ['session', 'overall_rating', 'therapist_rating', 'would_recommend', 'created_at']
    list_filter = ['overall_rating', 'would_recommend', 'created_at']
    search_fields = ['session__client__first_name', 'session__client__last_name', 'comments']
    readonly_fields = ['created_at']
    fieldsets = (
        ('اطلاعات رتبه‌بندی', {
            'fields': ('session', 'overall_rating', 'therapist_rating', 'environment_rating', 'helpfulness_rating')
        }),
        ('نظرات', {
            'fields': ('comments', 'would_recommend')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessionCancellation)
class SessionCancellationAdmin(admin.ModelAdmin):
    list_display = ['session', 'cancelled_by', 'reason', 'cancelled_at', 'is_refunded']
    list_filter = ['reason', 'is_refunded', 'cancelled_at']
    search_fields = ['session__client__first_name', 'session__client__last_name', 'explanation']
    readonly_fields = ['cancelled_at']
    fieldsets = (
        ('اطلاعات لغو', {
            'fields': ('session', 'cancelled_by', 'reason', 'explanation')
        }),
        ('بازپرداخت', {
            'fields': ('refund_amount', 'is_refunded')
        }),
        ('تاریخ‌ها', {
            'fields': ('cancelled_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessionReminder)
class SessionReminderAdmin(admin.ModelAdmin):
    list_display = ['session', 'reminder_type', 'scheduled_time', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'scheduled_time']
    search_fields = ['session__client__first_name', 'session__client__last_name']
    readonly_fields = ['created_at']
    fieldsets = (
        ('اطلاعات یادآوری', {
            'fields': ('session', 'reminder_type', 'scheduled_time')
        }),
        ('وضعیت ارسال', {
            'fields': ('is_sent', 'sent_at')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TherapistAvailability)
class TherapistAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['therapist', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available', 'created_at']
    search_fields = ['therapist__user__first_name', 'therapist__user__last_name']
    readonly_fields = ['created_at']
    fieldsets = (
        ('اطلاعات دسترسی', {
            'fields': ('therapist', 'day_of_week', 'start_time', 'end_time', 'is_available')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
