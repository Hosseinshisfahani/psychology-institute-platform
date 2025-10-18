from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    CourseCategory, Course, CourseModule, Lesson, 
    Enrollment, LessonProgress, CoursePurchase, CourseReview
)


class LessonInline(admin.TabularInline):
    """Inline admin for course lessons"""
    model = Lesson
    extra = 0
    fields = ['title', 'description', 'duration', 'order', 'is_published']


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for CourseCategory model"""
    
    list_display = ('name', 'slug', 'color', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model"""
    
    list_display = ('title', 'category', 'instructor', 'level', 'is_free', 'price', 'status', 'created_at')
    list_filter = ('status', 'level', 'is_free', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__first_name', 'instructor__last_name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'enrollment_count', 'rating', 'review_count')
    
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
            'fields': ('enrollment_count', 'rating', 'review_count'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    """Admin configuration for CourseModule model"""
    
    list_display = ('title', 'course', 'order', 'is_required')
    list_filter = ('is_required', 'course__category', 'course')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order')
    inlines = [LessonInline]


@admin.register(Lesson)
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


@admin.register(LessonProgress)
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


@admin.register(CourseReview)
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