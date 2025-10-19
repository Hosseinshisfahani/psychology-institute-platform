from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AdminDashboard(models.Model):
    """Admin dashboard configuration"""
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('داشبورد ادمین')
        verbose_name_plural = _('داشبوردهای ادمین')
    
    def __str__(self):
        return self.title


class AdminWidget(models.Model):
    """Dashboard widgets for admin panel"""
    
    WIDGET_TYPES = [
        ('stat', _('Statistics')),
        ('chart', _('Chart')),
        ('table', _('Table')),
        ('list', _('List')),
        ('custom', _('Custom')),
    ]
    
    dashboard = models.ForeignKey(AdminDashboard, on_delete=models.CASCADE, related_name='widgets', verbose_name='داشبورد')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name='نوع ویجت')
    position = models.PositiveIntegerField(default=0, verbose_name='موقعیت')
    size = models.CharField(max_length=20, default='medium', verbose_name='اندازه')
    config = models.JSONField(default=dict, verbose_name='پیکربندی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('ادمین ویجت')
        verbose_name_plural = _('ادمین ویجت ها')
        ordering = ['position']
    
    def __str__(self):
        return f"{self.title} - {self.dashboard.title}"


class AdminLog(models.Model):
    """Admin activity logs"""
    
    ACTION_TYPES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('export', _('Export')),
        ('import', _('Import')),
        ('backup', _('Backup')),
        ('restore', _('Restore')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs', verbose_name='کاربر')
    action = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name='عمل')
    model_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='نام مدل')
    object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name='شناسه شیء')
    description = models.TextField(verbose_name='توضیحات')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='آدرس IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='مرورگر کاربر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('لاگ ادمین')
        verbose_name_plural = _('لاگ های ادمین')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_action_display()} - {self.created_at}"


class AdminNotification(models.Model):
    """Admin notifications"""
    
    NOTIFICATION_TYPES = [
        ('info', _('Information')),
        ('warning', _('Warning')),
        ('error', _('Error')),
        ('success', _('Success')),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    message = models.TextField(verbose_name='پیام')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name='نوع')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    is_global = models.BooleanField(default=False, verbose_name='عمومی')
    target_users = models.ManyToManyField(User, blank=True, related_name='admin_notifications', verbose_name='کاربران هدف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ خواندن')
    
    class Meta:
        verbose_name = _('اعلان ادمین')
        verbose_name_plural = _('اعلان های ادمین')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class AdminSetting(models.Model):
    """Admin panel settings"""
    
    SETTING_TYPES = [
        ('general', _('General')),
        ('security', _('Security')),
        ('email', _('Email')),
        ('payment', _('Payment')),
        ('notification', _('Notification')),
        ('backup', _('Backup')),
    ]
    
    key = models.CharField(max_length=100, unique=True, verbose_name='کلید')
    value = models.TextField(verbose_name='مقدار')
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='general', verbose_name='نوع')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    is_encrypted = models.BooleanField(default=False, verbose_name='رمزگذاری شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('تنظیمات ادمین')
        verbose_name_plural = _('تنظیمات ادمین')
        ordering = ['setting_type', 'key']
    
    def __str__(self):
        return f"{self.key} - {self.get_setting_type_display()}"


class AdminBackup(models.Model):
    """Database backup records"""
    
    BACKUP_TYPES = [
        ('full', _('Full Backup')),
        ('incremental', _('Incremental Backup')),
        ('differential', _('Differential Backup')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('running', _('Running')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام')
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='full', verbose_name='نوع')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name='مسیر فایل')
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name='اندازه فایل')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_backups', verbose_name='ایجاد شده توسط')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='شروع شده در')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تکمیل شده در')
    error_message = models.TextField(blank=True, null=True, verbose_name='پیام خطا')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('پشتیبان ادمین')
        verbose_name_plural = _('پشتیبان های ادمین')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"