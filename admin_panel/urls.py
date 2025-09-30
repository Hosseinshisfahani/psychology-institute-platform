from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # User Management
    path('users/', views.AdminUsersView.as_view(), name='users'),
    
    # Order Management
    path('orders/', views.AdminOrdersView.as_view(), name='orders'),
    
    # Reports and Analytics
    path('reports/', views.AdminReportsView.as_view(), name='reports'),
    
    # Settings
    path('settings/', views.AdminSettingsView.as_view(), name='settings'),
    
    # Logs
    path('logs/', views.AdminLogsView.as_view(), name='logs'),
    
    # Notifications
    path('notifications/', views.AdminNotificationsView.as_view(), name='notifications'),
]
