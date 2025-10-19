from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Report(models.Model):
    """Financial and analytics reports"""
    
    REPORT_TYPES = [
        ('financial', _('Financial Report')),
        ('user_analytics', _('User Analytics')),
        ('course_analytics', _('Course Analytics')),
        ('test_analytics', _('Test Analytics')),
        ('session_analytics', _('Session Analytics')),
        ('sales', _('Sales Report')),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES, verbose_name='نوع گزارش')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    data = models.JSONField(default=dict, verbose_name='داده‌های گزارش')
    filters = models.JSONField(default=dict, verbose_name='فیلترهای اعمال شده')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports', verbose_name='ایجاد شده توسط')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    period_start = models.DateField(verbose_name='شروع دوره')
    period_end = models.DateField(verbose_name='پایان دوره')
    
    class Meta:
        verbose_name = _('گزارش')
        verbose_name_plural = _('گزارش‌ها')
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"


class DashboardWidget(models.Model):
    """Dashboard widgets for admin panel"""
    
    WIDGET_TYPES = [
        ('chart', _('Chart')),
        ('metric', _('Metric')),
        ('table', _('Table')),
        ('list', _('List')),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name='نوع ویجت')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    config = models.JSONField(default=dict, verbose_name='پیکربندی')
    position_x = models.PositiveIntegerField(default=0, verbose_name='موقعیت X')
    position_y = models.PositiveIntegerField(default=0, verbose_name='موقعیت Y')
    width = models.PositiveIntegerField(default=4, verbose_name='عرض')
    height = models.PositiveIntegerField(default=3, verbose_name='ارتفاع')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('ویجت داشبورد')
        verbose_name_plural = _('ویجت‌های داشبورد')
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return self.name


class AnalyticsEvent(models.Model):
    """Analytics events tracking"""
    
    EVENT_TYPES = [
        ('page_view', _('Page View')),
        ('course_enrollment', _('Course Enrollment')),
        ('test_completion', _('Test Completion')),
        ('session_booking', _('Session Booking')),
        ('payment', _('Payment')),
        ('user_registration', _('User Registration')),
        ('login', _('Login')),
        ('logout', _('Logout')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events', verbose_name='کاربر')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, verbose_name='نوع رویداد')
    event_data = models.JSONField(default=dict, verbose_name='داده‌های رویداد')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='آدرس IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='مرورگر کاربر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('رویداد تحلیل')
        verbose_name_plural = _('رویدادهای تحلیل')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.created_at}"