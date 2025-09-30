from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.NotificationReadView.as_view(), name='notification_read'),
    path('notifications/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
    
    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/preferences/', views.PreferencesView.as_view(), name='preferences'),
    
    # Statistics
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),
]

