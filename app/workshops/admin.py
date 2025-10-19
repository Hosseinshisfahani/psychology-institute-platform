from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
# from psychology_institute.admin import persian_admin_site
    WorkshopCategory, Workshop, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview
)

@admin.register(WorkshopCategory)
class WorkshopCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


class WorkshopSessionInline(admin.TabularInline):
    model = WorkshopSession
    extra = 1
    fields = ['session_number', 'title', 'scheduled_datetime', 'duration_minutes', 'is_completed']
    ordering = ['session_number']


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'instructor', 'status', 'start_date', 
        'current_participants', 'max_participants', 'price', 'created_at'
    ]
    list_filter = ['status', 'category', 'difficulty', 'payment_type', 'created_at']
    search_fields = ['title', 'description', 'instructor__first_name', 'instructor__last_name']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [WorkshopSessionInline]
    readonly_fields = ['current_participants', 'created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'category', 'instructor', 'status', 'difficulty')
        }),
        (_('Description'), {
            'fields': ('short_description', 'description', 'learning_objectives', 'prerequisites')
        }),
        (_('Scheduling'), {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        (_('Capacity'), {
            'fields': ('max_participants', 'current_participants')
        }),
        (_('Pricing'), {
            'fields': ('price', 'discount_price', 'payment_type', 'installment_months')
        }),
        (_('Details'), {
            'fields': ('total_hours', 'language')
        }),
        (_('Media'), {
            'fields': ('thumbnail', 'intro_video')
        }),
        (_('Statistics'), {
            'fields': ('rating', 'review_count')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_workshops', 'open_registration', 'generate_croom_links']
    
    def publish_workshops(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, _(f'{updated} workshops published successfully.'))
    publish_workshops.short_description = _('Publish selected workshops')
    
    def open_registration(self, request, queryset):
        updated = queryset.update(status='registration_open')
        self.message_user(request, _(f'{updated} workshops opened for registration.'))
    open_registration.short_description = _('Open registration for selected workshops')
    
    def generate_croom_links(self, request, queryset):
        from .services.croom_service import croom_service
        
        count = 0
        for workshop in queryset:
            for session in workshop.sessions.all():
                if not session.meeting_link:
                    session_data = {
                        'title': f"{workshop.title} - Session {session.session_number}",
                        'description': session.description or workshop.short_description,
                        'scheduled_datetime': session.scheduled_datetime,
                        'duration_minutes': session.duration_minutes,
                        'instructor_name': workshop.instructor.full_name,
                        'instructor_email': workshop.instructor.email,
                    }
                    
                    result = croom_service.create_meeting(session_data)
                    if result.get('success'):
                        session.meeting_id = result.get('meeting_id')
                        session.meeting_link = result.get('meeting_link')
                        session.meeting_password = result.get('meeting_password')
                        session.save()
                        count += 1
        
        self.message_user(request, _(f'Generated Croom links for {count} sessions.'))
    generate_croom_links.short_description = _('Generate Croom meeting links for sessions')


@admin.register(WorkshopSession)
class WorkshopSessionAdmin(admin.ModelAdmin):
    list_display = [
        'workshop', 'session_number', 'title', 'scheduled_datetime', 
        'duration_minutes', 'has_meeting_link', 'is_completed'
    ]
    list_filter = ['workshop', 'is_completed', 'scheduled_datetime']
    search_fields = ['title', 'description', 'workshop__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('workshop', 'session_number', 'title', 'description')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_datetime', 'duration_minutes')
        }),
        (_('Croom Integration'), {
            'fields': ('meeting_link', 'meeting_id', 'meeting_password', 'recording_url')
        }),
        (_('Materials'), {
            'fields': ('materials', 'homework')
        }),
        (_('Status'), {
            'fields': ('is_completed', 'completed_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_meeting_link(self, obj):
        return bool(obj.meeting_link)
    has_meeting_link.boolean = True
    has_meeting_link.short_description = _('Has Meeting Link')


class InstallmentPaymentInline(admin.TabularInline):
    model = InstallmentPayment
    extra = 0
    readonly_fields = ['installment_number', 'due_date', 'status', 'paid_at']
    can_delete = False


@admin.register(WorkshopRegistration)
class WorkshopRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'workshop', 'status', 'payment_type', 
        'amount_paid', 'total_amount', 'progress_percentage', 'registered_at'
    ]
    list_filter = ['status', 'payment_type', 'registered_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'workshop__title']
    readonly_fields = ['registered_at', 'completed_at', 'last_accessed', 'progress_percentage']
    
    fieldsets = (
        (_('Registration'), {
            'fields': ('user', 'workshop', 'status', 'payment_type')
        }),
        (_('Payment'), {
            'fields': ('amount_paid', 'total_amount')
        }),
        (_('Progress'), {
            'fields': ('progress_percentage',)
        }),
        (_('Timestamps'), {
            'fields': ('registered_at', 'completed_at', 'last_accessed')
        }),
    )


@admin.register(WorkshopSessionAttendance)
class WorkshopSessionAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'user_name', 'session', 'attended', 'join_time', 
        'leave_time', 'duration_minutes', 'attendance_marked_at'
    ]
    list_filter = ['attended', 'session__workshop', 'attendance_marked_at']
    search_fields = [
        'registration__user__email', 
        'registration__user__first_name', 
        'registration__user__last_name',
        'session__title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def user_name(self, obj):
        return obj.registration.user.full_name
    user_name.short_description = _('User')


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = [
        'registration', 'total_amount', 'number_of_installments', 
        'installment_amount', 'total_paid', 'remaining_amount', 'is_fully_paid'
    ]
    list_filter = ['created_at']
    search_fields = [
        'registration__user__email', 
        'registration__user__first_name',
        'registration__workshop__title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'total_paid', 'remaining_amount', 'is_fully_paid']
    inlines = [InstallmentPaymentInline]


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'plan', 'installment_number', 'amount', 'due_date', 
        'status', 'paid_at', 'reminder_sent'
    ]
    list_filter = ['status', 'due_date', 'reminder_sent', 'paid_at']
    search_fields = [
        'plan__registration__user__email',
        'plan__registration__user__first_name',
        'plan__registration__workshop__title',
        'transaction_id'
    ]
    readonly_fields = ['created_at', 'updated_at', 'reminder_sent_at']
    
    fieldsets = (
        (_('Plan'), {
            'fields': ('plan', 'installment_number')
        }),
        (_('Payment'), {
            'fields': ('amount', 'due_date', 'status')
        }),
        (_('Payment Details'), {
            'fields': ('paid_at', 'payment_method', 'transaction_id', 'order')
        }),
        (_('Reminders'), {
            'fields': ('reminder_sent', 'reminder_sent_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkshopReview)
class WorkshopReviewAdmin(admin.ModelAdmin):
    list_display = [
        'workshop_title', 'user_name', 'rating', 
        'is_approved', 'created_at'
    ]
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = [
        'registration__user__email',
        'registration__user__first_name',
        'registration__workshop__title',
        'title', 'content'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Review'), {
            'fields': ('registration', 'rating', 'title', 'content')
        }),
        (_('Detailed Ratings'), {
            'fields': ('instructor_rating', 'content_rating', 'interaction_rating')
        }),
        (_('Moderation'), {
            'fields': ('is_approved',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def workshop_title(self, obj):
        return obj.registration.workshop.title
    workshop_title.short_description = _('Workshop')
    
    def user_name(self, obj):
        return obj.registration.user.full_name
    user_name.short_description = _('User')
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f'{updated} reviews approved.'))
    approve_reviews.short_description = _('Approve selected reviews')
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(f'{updated} reviews rejected.'))
    reject_reviews.short_description = _('Reject selected reviews')
