from django.contrib import admin
from .models import (
# from psychology_institute.admin import persian_admin_site
    Cohort, CohortSession, CohortEnrollment, 
    CohortInstallment, CohortAttendance
)


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'start_date', 'status', 'current_enrollments', 'max_students']
    list_filter = ['status', 'is_active', 'start_date', 'instructor']
    search_fields = ['title', 'description', 'instructor__first_name', 'instructor__last_name']
    readonly_fields = ['current_enrollments']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'class_time', 'duration_minutes', 'total_sessions')
        }),
        ('Pricing', {
            'fields': ('full_price', 'installment_3_price', 'installment_6_price')
        }),
        ('Capacity', {
            'fields': ('max_students', 'current_enrollments')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        })
    )


@admin.register(CohortSession)
class CohortSessionAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'session_number', 'title', 'scheduled_date', 'is_completed', 'is_recording_available']
    list_filter = ['is_completed', 'is_recording_available', 'scheduled_date', 'cohort']
    search_fields = ['title', 'description', 'cohort__title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Session Information', {
            'fields': ('cohort', 'session_number', 'title', 'description')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time', 'duration_minutes')
        }),
        ('Completion', {
            'fields': ('is_completed', 'actual_start_time', 'actual_end_time', 'notes')
        }),
        ('Recording', {
            'fields': ('recording_file', 'recording_url', 'is_recording_available')
        })
    )


@admin.register(CohortEnrollment)
class CohortEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'cohort', 'status', 'payment_type', 'payment_status', 'total_amount', 'amount_paid']
    list_filter = ['status', 'payment_type', 'payment_status', 'enrolled_at']
    search_fields = ['student__first_name', 'student__last_name', 'cohort__title']
    readonly_fields = ['enrolled_at', 'remaining_amount']
    fieldsets = (
        ('Enrollment', {
            'fields': ('student', 'cohort', 'status')
        }),
        ('Payment', {
            'fields': ('payment_type', 'payment_status', 'total_amount', 'amount_paid', 'remaining_amount')
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'confirmed_at', 'completed_at')
        })
    )


@admin.register(CohortInstallment)
class CohortInstallmentAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'installment_number', 'amount', 'due_date', 'status', 'paid_at']
    list_filter = ['status', 'due_date', 'enrollment__cohort']
    search_fields = ['enrollment__student__first_name', 'enrollment__student__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Installment', {
            'fields': ('enrollment', 'installment_number', 'amount', 'due_date', 'status')
        }),
        ('Payment', {
            'fields': ('paid_at', 'payment_method', 'transaction_id')
        })
    )


@admin.register(CohortAttendance)
class CohortAttendanceAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'session', 'is_present', 'arrived_at']
    list_filter = ['is_present', 'session__cohort', 'session__scheduled_date']
    search_fields = ['enrollment__student__first_name', 'enrollment__student__last_name', 'session__title']
    readonly_fields = ['created_at', 'updated_at']
