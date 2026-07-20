from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    CourseCategory, Course, CourseVideo, CourseModule, Lesson, 
    Enrollment, LessonProgress, CoursePurchase, CourseReview, Coupon,
    CourseLike, CourseComment
)


class CourseVideoInline(admin.TabularInline):
    """Inline admin for course videos"""
    model = CourseVideo
    extra = 1
    fields = ['title', 'description', 'video_file', 'video_url', 'attachment_file', 'duration_minutes', 'order', 'is_preview', 'allow_download', 'is_active']

'''
class LessonInline(admin.TabularInline):
    """Inline admin for course lessons"""
    model = Lesson
    extra = 0
    fields = ['title', 'description', 'duration', 'order', 'is_published']
'''

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for CourseCategory model"""
    
    list_display = ('name', 'slug', 'color', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)


@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    """Admin configuration for CourseVideo model"""
    
    list_display = ('title', 'course', 'order', 'duration_minutes', 'is_preview', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_preview', 'allow_download', 'created_at', 'course__category')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'description', 'order')
        }),
        (_('Video'), {
            'fields': ('video_file', 'video_url', 'duration_minutes')
        }),
        (_('Attachment'), {
            'fields': ('attachment_file',),
            'description': _('فایل پیوست برای ویدیو (مثل PDF، فایل تمرین، و غیره)')
        }),
        (_('Settings'), {
            'fields': ('is_preview', 'allow_download', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model"""
    
    list_display = ('title', 'category', 'instructor', 'level', 'is_free', 'price', 'status', 'created_at')
    list_filter = ('status', 'level', 'is_free', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__first_name', 'instructor__last_name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'enrollment_count', 'rating', 'review_count', 'like_count')
    inlines = [CourseVideoInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'category', 'instructor')
        }),
        (_('Course Configuration'), {
            'fields': ('level', 'duration_hours', 'learning_objectives', 'prerequisites')
        }),
        (_('Pricing'), {
            'fields': ('is_free', 'price')
        }),
        (_('Content'), {
            'fields': ('thumbnail', 'video_intro')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Statistics'), {
            'fields': ('enrollment_count', 'rating', 'review_count', 'like_count'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


'''@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    """Admin configuration for CourseModule model"""
    
    list_display = ('title', 'course', 'order', 'is_required')
    list_filter = ('is_required', 'course__category', 'course')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order')
#    inlines = [LessonInline]
'''

'''@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin configuration for Lesson model"""
    
    list_display = ('title', 'module', 'duration_minutes', 'order', 'is_required')
    list_filter = ('is_required', 'lesson_type', 'module__course__category', 'module__course')
    search_fields = ('title', 'description', 'module__title', 'module__course__title')
    ordering = ('module__course', 'module__order', 'order')
    
    fieldsets = (
        (None, {
            'fields': ('module', 'title', 'description', 'order')
        }),
        (_('Content'), {
            'fields': ('content', 'video_file', 'video_url')
        }),
        (_('Settings'), {
            'fields': ('duration_minutes', 'is_required', 'is_preview')
        }),
    )
'''

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for Enrollment model"""
    
    list_display = ('user', 'course', 'enrolled_at', 'status', 'completed_at')
    list_filter = ('status', 'enrolled_at', 'completed_at', 'course__category')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'course__title')
    readonly_fields = ('enrolled_at', 'completed_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'course')
        }),
        (_('Progress'), {
            'fields': ('status', 'progress_percentage')
        }),
        (_('Timestamps'), {
            'fields': ('enrolled_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


'''@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    """Admin configuration for LessonProgress model"""
    
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'lesson__module__course__category')
    search_fields = ('enrollment__user__first_name', 'enrollment__user__last_name', 'lesson__title')
    readonly_fields = ('completed_at',)
    
    fieldsets = (
        (None, {
            'fields': ('enrollment', 'lesson')
        }),
        (_('Progress'), {
            'fields': ('is_completed', 'time_spent')
        }),
        (_('Timestamp'), {
            'fields': ('completed_at',),
            'classes': ('collapse',)
        }),
    )
'''

@admin.register(CoursePurchase)
class CoursePurchaseAdmin(admin.ModelAdmin):
    """Admin configuration for CoursePurchase model"""
    
    list_display = ('user', 'course', 'amount_paid', 'purchased_at', 'payment_method')
    list_filter = ('payment_method', 'purchased_at', 'course__category')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'course__title', 'transaction_id')
    readonly_fields = ('purchased_at',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'course', 'amount_paid')
        }),
        (_('Payment'), {
            'fields': ('payment_method', 'transaction_id')
        }),
        (_('Timestamp'), {
            'fields': ('purchased_at',),
            'classes': ('collapse',)
        }),
    )


'''@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    """Admin configuration for CourseReview model"""
    
    list_display = ('enrollment', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at', 'enrollment__course__category')
    search_fields = ('enrollment__user__first_name', 'enrollment__user__last_name', 'enrollment__course__title', 'content')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('enrollment', 'rating')
        }),
        (_('Review'), {
            'fields': ('title', 'content', 'is_approved')
        }),
        (_('Timestamp'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
'''


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin configuration for Coupon model"""
    
    list_display = ('code', 'title', 'coupon_type', 'discount_value', 'is_active', 'valid_from', 'valid_until', 'used_count', 'usage_limit')
    list_filter = ('coupon_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'title', 'description')
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    filter_horizontal = ('applicable_courses',)
    
    fieldsets = (
        (None, {
            'fields': ('code', 'title', 'description')
        }),
        (_('Discount'), {
            'fields': ('coupon_type', 'discount_value', 'min_order_amount', 'max_discount_amount')
        }),
        (_('Usage Limits'), {
            'fields': ('usage_limit', 'used_count')
        }),
        (_('Validity'), {
            'fields': ('is_active', 'valid_from', 'valid_until')
        }),
        (_('Applicable Courses'), {
            'fields': ('applicable_courses',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CourseLike)
class CourseLikeAdmin(admin.ModelAdmin):
    """Admin configuration for CourseLike model"""
    
    list_display = ('course', 'user', 'created_at')
    list_filter = ('created_at', 'course__category')
    search_fields = ('course__title', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'user')


@admin.register(CourseComment)
class CourseCommentAdmin(admin.ModelAdmin):
    """Admin configuration for CourseComment model"""
    
    list_display = ('course', 'author', 'is_approved', 'created_at', 'replies_count')
    list_filter = ('is_approved', 'created_at', 'course__category')
    search_fields = ('course__title', 'author__first_name', 'author__last_name', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('course', 'author', 'content', 'parent')
        }),
        (_('Moderation'), {
            'fields': ('is_approved',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_comments', 'reject_comments']
    
    def replies_count(self, obj):
        return obj.replies.count()
    replies_count.short_description = _('Replies')
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f'{updated} comments approved.'))
    approve_comments.short_description = _('Approve selected comments')
    
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(f'{updated} comments rejected.'))
    reject_comments.short_description = _('Reject selected comments')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'author', 'parent')