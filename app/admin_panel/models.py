from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AdminDashboard(models.Model):
    """Admin dashboard configuration"""
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Admin Dashboard')
        verbose_name_plural = _('Admin Dashboards')
    
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
    
    dashboard = models.ForeignKey(AdminDashboard, on_delete=models.CASCADE, related_name='widgets', verbose_name=_('Dashboard'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name=_('Widget Type'))
    position = models.PositiveIntegerField(default=0, verbose_name=_('Position'))
    size = models.CharField(max_length=20, default='medium', verbose_name=_('Size'))
    config = models.JSONField(default=dict, verbose_name=_('Configuration'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Admin Widget')
        verbose_name_plural = _('Admin Widgets')
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs', verbose_name=_('User'))
    action = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name=_('Action'))
    model_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Model Name'))
    object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Object ID'))
    description = models.TextField(verbose_name=_('Description'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('IP Address'))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_('User Agent'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Admin Log')
        verbose_name_plural = _('Admin Logs')
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
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    message = models.TextField(verbose_name=_('Message'))
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name=_('Type'))
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))
    is_global = models.BooleanField(default=False, verbose_name=_('Is Global'))
    target_users = models.ManyToManyField(User, blank=True, related_name='admin_notifications', verbose_name=_('Target Users'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Read At'))
    
    class Meta:
        verbose_name = _('Admin Notification')
        verbose_name_plural = _('Admin Notifications')
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
    
    key = models.CharField(max_length=100, unique=True, verbose_name=_('Key'))
    value = models.TextField(verbose_name=_('Value'))
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='general', verbose_name=_('Type'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    is_encrypted = models.BooleanField(default=False, verbose_name=_('Is Encrypted'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Admin Setting')
        verbose_name_plural = _('Admin Settings')
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
    
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='full', verbose_name=_('Type'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('File Path'))
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name=_('File Size'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_backups', verbose_name=_('Created By'))
    started_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Started At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    error_message = models.TextField(blank=True, null=True, verbose_name=_('Error Message'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Admin Backup')
        verbose_name_plural = _('Admin Backups')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"