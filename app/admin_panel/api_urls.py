from django.urls import path
from .api_views import (
    DashboardStatsAPIView, AdminUserListAPIView, AdminUserDetailAPIView,
    AdminPostListAPIView, AdminPostDetailAPIView, AdminCourseListAPIView,
    AdminCourseDetailAPIView, AdminActivityListAPIView,
    AdminNotificationListAPIView, toggle_user_status, bulk_user_action,
    admin_analytics, send_notification, export_users, bulk_course_action,
    # AdminSessionListAPIView, AdminAppointmentListAPIView, AdminAppointmentDetailAPIView, confirm_appointment,  # Removed - therapy_sessions app deleted
    # reject_appointment, AdminTherapistListAPIView, AdminTherapistDetailAPIView,  # Removed - therapy_sessions app deleted
    # AdminSessionTypeListAPIView, AdminSessionTypeDetailAPIView,  # Removed - therapy_sessions app deleted
    AdminBlogPostListAPIView, AdminBlogPostDetailAPIView, bulk_blog_post_action,
    AdminBlogCategoryListAPIView, AdminBlogCategoryDetailAPIView,
    AdminBlogTagListAPIView, AdminBlogTagDetailAPIView,
    AdminBlogCommentListAPIView, AdminBlogCommentDetailAPIView, bulk_blog_comment_action,
    AdminWorkshopListAPIView, AdminWorkshopDetailAPIView, AdminWorkshopSessionListAPIView,
    AdminWorkshopSessionDetailAPIView, AdminWorkshopRegistrationListAPIView,
    bulk_workshop_action, generate_croom_meeting_link, approve_workshop_registration,
    reject_workshop_registration, AdminPackageListAPIView, AdminPackageDetailAPIView,
    AdminPackageCategoryListAPIView, AdminPackageCategoryDetailAPIView, bulk_package_action
)
from .upload_api import upload_file

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api_admin_dashboard_stats'),
    path('analytics/', admin_analytics, name='api_admin_analytics'),
    
    # Users
    path('users/', AdminUserListAPIView.as_view(), name='api_admin_users'),
    path('users/<int:pk>/', AdminUserDetailAPIView.as_view(), name='api_admin_user_detail'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='api_toggle_user_status'),
    path('users/bulk-action/', bulk_user_action, name='api_bulk_user_action'),
    path('users/export/', export_users, name='api_export_users'),
    
    # Posts
    path('posts/', AdminPostListAPIView.as_view(), name='api_admin_posts'),
    path('posts/<int:pk>/', AdminPostDetailAPIView.as_view(), name='api_admin_post_detail'),
    
    # Courses
    path('courses/', AdminCourseListAPIView.as_view(), name='api_admin_courses'),
    path('courses/<int:pk>/', AdminCourseDetailAPIView.as_view(), name='api_admin_course_detail'),
    path('courses/bulk-action/', bulk_course_action, name='api_bulk_course_action'),
    
    # Sessions - commented out due to therapy_sessions app deletion
    # path('sessions/', AdminSessionListAPIView.as_view(), name='api_admin_sessions'),
    
    # Activities and Notifications
    path('activities/', AdminActivityListAPIView.as_view(), name='api_admin_activities'),
    path('notifications/', AdminNotificationListAPIView.as_view(), name='api_admin_notifications'),
    path('notifications/send/', send_notification, name='api_send_notification'),
    
    # Appointment Management - commented out due to therapy_sessions app deletion
    # path('appointments/', AdminAppointmentListAPIView.as_view(), name='api_admin_appointments'),
    # path('appointments/<int:pk>/', AdminAppointmentDetailAPIView.as_view(), name='api_admin_appointment_detail'),
    # path('appointments/<int:appointment_id>/confirm/', confirm_appointment, name='api_confirm_appointment'),
    # path('appointments/<int:appointment_id>/reject/', reject_appointment, name='api_reject_appointment'),
    
    # Therapist Management - commented out due to therapy_sessions app deletion
    # path('therapists/', AdminTherapistListAPIView.as_view(), name='api_admin_therapists'),
    # path('therapists/<int:pk>/', AdminTherapistDetailAPIView.as_view(), name='api_admin_therapist_detail'),
    
    # Session Types Management - commented out due to therapy_sessions app deletion
    # path('session-types/', AdminSessionTypeListAPIView.as_view(), name='api_admin_session_types'),
    # path('session-types/<int:pk>/', AdminSessionTypeDetailAPIView.as_view(), name='api_admin_session_type_detail'),
    
    # Blog Management
    path('blog/posts/', AdminBlogPostListAPIView.as_view(), name='api_admin_blog_posts'),
    path('blog/posts/<int:pk>/', AdminBlogPostDetailAPIView.as_view(), name='api_admin_blog_post_detail'),
    path('blog/posts/bulk-action/', bulk_blog_post_action, name='api_bulk_blog_post_action'),
    
    # Blog Categories
    path('blog/categories/', AdminBlogCategoryListAPIView.as_view(), name='api_admin_blog_categories'),
    path('blog/categories/<int:pk>/', AdminBlogCategoryDetailAPIView.as_view(), name='api_admin_blog_category_detail'),
    
    # Blog Tags
    path('blog/tags/', AdminBlogTagListAPIView.as_view(), name='api_admin_blog_tags'),
    path('blog/tags/<int:pk>/', AdminBlogTagDetailAPIView.as_view(), name='api_admin_blog_tag_detail'),
    
    # Blog Comments
    path('blog/comments/', AdminBlogCommentListAPIView.as_view(), name='api_admin_blog_comments'),
    path('blog/comments/<int:pk>/', AdminBlogCommentDetailAPIView.as_view(), name='api_admin_blog_comment_detail'),
    path('blog/comments/bulk-action/', bulk_blog_comment_action, name='api_bulk_blog_comment_action'),
    
    # Workshop Management
    path('workshops/', AdminWorkshopListAPIView.as_view(), name='api_admin_workshops'),
    path('workshops/<int:pk>/', AdminWorkshopDetailAPIView.as_view(), name='api_admin_workshop_detail'),
    path('workshops/bulk-action/', bulk_workshop_action, name='api_bulk_workshop_action'),
    
    # Workshop Sessions
    path('workshops/<int:workshop_id>/sessions/', AdminWorkshopSessionListAPIView.as_view(), name='api_admin_workshop_sessions'),
    path('workshops/<int:workshop_id>/sessions/<int:pk>/', AdminWorkshopSessionDetailAPIView.as_view(), name='api_admin_workshop_session_detail'),
    path('workshops/sessions/<int:session_id>/generate-croom-link/', generate_croom_meeting_link, name='api_generate_croom_meeting_link'),
    
    # Workshop Registrations
    path('workshops/<int:workshop_id>/registrations/', AdminWorkshopRegistrationListAPIView.as_view(), name='api_admin_workshop_registrations'),
    path('workshops/registrations/<int:registration_id>/approve/', approve_workshop_registration, name='api_approve_workshop_registration'),
    path('workshops/registrations/<int:registration_id>/reject/', reject_workshop_registration, name='api_reject_workshop_registration'),
    
    # Package Management
    path('packages/', AdminPackageListAPIView.as_view(), name='api_admin_packages'),
    path('packages/<int:pk>/', AdminPackageDetailAPIView.as_view(), name='api_admin_package_detail'),
    path('packages/bulk-action/', bulk_package_action, name='api_bulk_package_action'),
    path('packages/categories/', AdminPackageCategoryListAPIView.as_view(), name='api_admin_package_categories'),
    path('packages/categories/<int:pk>/', AdminPackageCategoryDetailAPIView.as_view(), name='api_admin_package_category_detail'),
    
    # File Upload
    path('upload/', upload_file, name='api_upload_file'),
]
