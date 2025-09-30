from django.urls import path
from .api_views import (
    DashboardStatsAPIView, AdminUserListAPIView, AdminUserDetailAPIView,
    AdminPostListAPIView, AdminPostDetailAPIView, AdminCourseListAPIView,
    AdminCourseDetailAPIView, AdminSessionListAPIView, AdminActivityListAPIView,
    AdminNotificationListAPIView, toggle_user_status, bulk_user_action,
    admin_analytics, send_notification
)

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api_admin_dashboard_stats'),
    path('analytics/', admin_analytics, name='api_admin_analytics'),
    
    # Users
    path('users/', AdminUserListAPIView.as_view(), name='api_admin_users'),
    path('users/<int:pk>/', AdminUserDetailAPIView.as_view(), name='api_admin_user_detail'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='api_toggle_user_status'),
    path('users/bulk-action/', bulk_user_action, name='api_bulk_user_action'),
    
    # Posts
    path('posts/', AdminPostListAPIView.as_view(), name='api_admin_posts'),
    path('posts/<int:pk>/', AdminPostDetailAPIView.as_view(), name='api_admin_post_detail'),
    
    # Courses
    path('courses/', AdminCourseListAPIView.as_view(), name='api_admin_courses'),
    path('courses/<int:pk>/', AdminCourseDetailAPIView.as_view(), name='api_admin_course_detail'),
    
    # Sessions
    path('sessions/', AdminSessionListAPIView.as_view(), name='api_admin_sessions'),
    
    # Activities and Notifications
    path('activities/', AdminActivityListAPIView.as_view(), name='api_admin_activities'),
    path('notifications/', AdminNotificationListAPIView.as_view(), name='api_admin_notifications'),
    path('notifications/send/', send_notification, name='api_send_notification'),
]
