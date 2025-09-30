from django.urls import path
from . import api_views

app_name = 'dashboard_api'

urlpatterns = [
    # User profile
    path('profile/', api_views.UserProfileView.as_view(), name='user_profile'),
    
    # Dashboard data
    path('stats/', api_views.dashboard_stats, name='dashboard_stats'),
    path('activities/', api_views.recent_activities, name='recent_activities'),
    
    # User data
    path('enrollments/', api_views.user_enrollments, name='user_enrollments'),
    path('test-results/', api_views.user_test_results, name='user_test_results'),
    path('sessions/', api_views.user_sessions, name='user_sessions'),
    
    # Notifications
    path('notifications/', api_views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:notification_id>/read/', api_views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', api_views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
