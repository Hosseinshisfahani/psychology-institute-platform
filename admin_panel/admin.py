from django.contrib import admin
from .models import AdminDashboard, AdminWidget, AdminLog, AdminNotification, AdminSetting, AdminBackup


@admin.register(AdminDashboard)
class AdminDashboardAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminWidget)
class AdminWidgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'dashboard', 'widget_type', 'position', 'is_active']
    list_filter = ['widget_type', 'is_active', 'dashboard']
    search_fields = ['title']
    ordering = ['dashboard', 'position']


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'created_at']
    list_filter = ['action', 'created_at', 'user']
    search_fields = ['user__first_name', 'user__last_name', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'is_read', 'is_global', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_global', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'read_at']


@admin.register(AdminSetting)
class AdminSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'setting_type', 'is_encrypted', 'updated_at']
    list_filter = ['setting_type', 'is_encrypted']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminBackup)
class AdminBackupAdmin(admin.ModelAdmin):
    list_display = ['name', 'backup_type', 'status', 'file_size', 'created_by', 'created_at']
    list_filter = ['backup_type', 'status', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'started_at', 'completed_at']