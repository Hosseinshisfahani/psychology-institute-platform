from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
# from psychology_institute.admin import persian_admin_site
    PackageCategory, Package, PackagePurchase, PackageEnrollment,
    PackageProgress, PackageReview, PackageCoupon
)


@admin.register(PackageCategory)
class PackageCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


class PackageEnrollmentInline(admin.TabularInline):
    model = PackageEnrollment
    extra = 0
    readonly_fields = ['enrollment', 'started_at', 'last_accessed', 'progress_percentage']
    can_delete = False
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage:.1f}%"
    progress_percentage.short_description = _('Progress')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'status', 'total_courses', 
        'price', 'discount_price', 'purchase_count', 'rating', 'is_featured'
    ]
    list_filter = ['status', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['courses']
    readonly_fields = ['purchase_count', 'created_at', 'updated_at', 'published_at', 'total_courses_display']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'category', 'status', 'is_featured')
        }),
        (_('Description'), {
            'fields': ('short_description', 'description', 'learning_objectives', 'prerequisites')
        }),
        (_('Courses'), {
            'fields': ('courses', 'total_courses_display')
        }),
        (_('Pricing'), {
            'fields': ('price', 'discount_price')
        }),
        (_('Details'), {
            'fields': ('duration_months', 'language')
        }),
        (_('Media'), {
            'fields': ('thumbnail', 'intro_video')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('purchase_count', 'rating', 'review_count')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_packages', 'archive_packages', 'feature_packages']
    
    def total_courses_display(self, obj):
        return obj.total_courses
    total_courses_display.short_description = _('Total Courses')
    
    def publish_packages(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, _(f'{updated} packages published successfully.'))
    publish_packages.short_description = _('Publish selected packages')
    
    def archive_packages(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, _(f'{updated} packages archived.'))
    archive_packages.short_description = _('Archive selected packages')
    
    def feature_packages(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, _(f'{updated} packages marked as featured.'))
    feature_packages.short_description = _('Mark as featured')


@admin.register(PackagePurchase)
class PackagePurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'package', 'amount_paid', 'purchased_at', 'is_expired'
    ]
    list_filter = ['purchased_at', 'expires_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 
        'package__title', 'transaction_id'
    ]
    readonly_fields = ['purchased_at']
    inlines = [PackageEnrollmentInline]
    
    fieldsets = (
        (_('Purchase'), {
            'fields': ('user', 'package', 'purchased_at', 'expires_at')
        }),
        (_('Payment'), {
            'fields': ('amount_paid', 'original_price', 'discount_amount', 'payment_method', 'transaction_id', 'order')
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Expired')


@admin.register(PackageEnrollment)
class PackageEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'user_name', 'package_title', 'course_title', 
        'progress_display', 'started_at', 'last_accessed'
    ]
    list_filter = ['purchase__package', 'started_at']
    search_fields = [
        'purchase__user__email',
        'purchase__user__first_name',
        'purchase__package__title',
        'enrollment__course__title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'progress_display']
    
    def user_name(self, obj):
        return obj.purchase.user.full_name
    user_name.short_description = _('User')
    
    def package_title(self, obj):
        return obj.purchase.package.title
    package_title.short_description = _('Package')
    
    def course_title(self, obj):
        return obj.enrollment.course.title
    course_title.short_description = _('Course')
    
    def progress_display(self, obj):
        return f"{obj.progress_percentage:.1f}%"
    progress_display.short_description = _('Progress')


@admin.register(PackageProgress)
class PackageProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user_name', 'package_title', 'overall_progress_display',
        'completed_courses', 'updated_at'
    ]
    list_filter = ['updated_at']
    search_fields = [
        'purchase__user__email',
        'purchase__user__first_name',
        'purchase__package__title'
    ]
    readonly_fields = ['updated_at']
    
    def user_name(self, obj):
        return obj.purchase.user.full_name
    user_name.short_description = _('User')
    
    def package_title(self, obj):
        return obj.purchase.package.title
    package_title.short_description = _('Package')
    
    def overall_progress_display(self, obj):
        return f"{obj.overall_progress_percentage:.1f}%"
    overall_progress_display.short_description = _('Overall Progress')


@admin.register(PackageReview)
class PackageReviewAdmin(admin.ModelAdmin):
    list_display = [
        'package_title', 'user_name', 'rating',
        'is_approved', 'created_at'
    ]
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = [
        'purchase__user__email',
        'purchase__user__first_name',
        'purchase__package__title',
        'title', 'content'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Review'), {
            'fields': ('purchase', 'rating', 'title', 'content')
        }),
        (_('Detailed Ratings'), {
            'fields': ('value_rating', 'content_rating', 'support_rating')
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
    
    def package_title(self, obj):
        return obj.purchase.package.title
    package_title.short_description = _('Package')
    
    def user_name(self, obj):
        return obj.purchase.user.full_name
    user_name.short_description = _('User')
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f'{updated} reviews approved.'))
    approve_reviews.short_description = _('Approve selected reviews')
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(f'{updated} reviews rejected.'))
    reject_reviews.short_description = _('Reject selected reviews')


@admin.register(PackageCoupon)
class PackageCouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'title', 'coupon_type', 'discount_value',
        'usage_status', 'is_active', 'valid_from', 'valid_until'
    ]
    list_filter = ['coupon_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'title', 'description']
    filter_horizontal = ['applicable_packages']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'title', 'description')
        }),
        (_('Discount'), {
            'fields': ('coupon_type', 'discount_value', 'min_order_amount', 'max_discount_amount')
        }),
        (_('Usage'), {
            'fields': ('usage_limit', 'used_count')
        }),
        (_('Validity'), {
            'fields': ('is_active', 'valid_from', 'valid_until')
        }),
        (_('Applicable Packages'), {
            'fields': ('applicable_packages',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def usage_status(self, obj):
        if obj.usage_limit:
            return f"{obj.used_count}/{obj.usage_limit}"
        return f"{obj.used_count}/∞"
    usage_status.short_description = _('Usage')
    
    actions = ['activate_coupons', 'deactivate_coupons']
    
    def activate_coupons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} coupons activated.'))
    activate_coupons.short_description = _('Activate selected coupons')
    
    def deactivate_coupons(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} coupons deactivated.'))
    deactivate_coupons.short_description = _('Deactivate selected coupons')
