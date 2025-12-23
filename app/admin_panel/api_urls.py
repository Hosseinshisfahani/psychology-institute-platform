from django.urls import path
from .api_views import (
    DashboardStatsAPIView, AdminUserListAPIView, AdminUserDetailAPIView,
    AdminPostListAPIView, AdminPostDetailAPIView, AdminCourseListAPIView,
    AdminCourseDetailAPIView, AdminActivityListAPIView,
    AdminNotificationListAPIView, admin_notification_count, mark_notification_read,
    mark_notification_unread, mark_all_notifications_read, delete_notification,
    toggle_user_status, bulk_user_action, admin_analytics, send_notification, export_users, bulk_course_action,
    # AdminSessionListAPIView, AdminAppointmentListAPIView, AdminAppointmentDetailAPIView, confirm_appointment,  # Removed - therapy_sessions app deleted
    # reject_appointment, AdminTherapistListAPIView, AdminTherapistDetailAPIView,  # Removed - therapy_sessions app deleted
    # AdminSessionTypeListAPIView, AdminSessionTypeDetailAPIView,  # Removed - therapy_sessions app deleted
    AdminBlogPostListAPIView, AdminBlogPostDetailAPIView, bulk_blog_post_action,
    AdminBlogCategoryListAPIView, AdminBlogCategoryDetailAPIView,
    AdminBlogTagListAPIView, AdminBlogTagDetailAPIView,
    AdminBlogCommentListAPIView, AdminBlogCommentDetailAPIView, bulk_blog_comment_action,
    AdminCourseCommentListAPIView, AdminCourseCommentDetailAPIView, bulk_course_comment_action,
    AdminWorkshopListAPIView, AdminWorkshopDetailAPIView, AdminWorkshopSessionListAPIView,
    AdminWorkshopSessionDetailAPIView, AdminWorkshopRegistrationListAPIView,
    AdminWorkshopCategoryListAPIView, AdminWorkshopCategoryDetailAPIView,
    AdminWorkshopReviewListAPIView, AdminWorkshopReviewDetailAPIView, bulk_workshop_review_action,
    bulk_workshop_action, approve_workshop_registration,
    reject_workshop_registration, AdminPackageListAPIView, AdminPackageDetailAPIView,
    AdminPackageCategoryListAPIView, AdminPackageCategoryDetailAPIView, bulk_package_action,
    AdminPackageCommentListAPIView, AdminPackageCommentDetailAPIView, bulk_package_comment_action,
    admin_payments_overview, admin_payments_revenue_series, admin_recent_payments,
    admin_user_financial_logs
)
from .upload_api import upload_file

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api_admin_dashboard_stats'),
    path('analytics/', admin_analytics, name='api_admin_analytics'),
    # Payments Analytics
    path('payments/overview/', admin_payments_overview, name='api_admin_payments_overview'),
    path('payments/revenue-series/', admin_payments_revenue_series, name='api_admin_payments_revenue_series'),
    path('payments/recent/', admin_recent_payments, name='api_admin_recent_payments'),
    
    # Users
    path('users/', AdminUserListAPIView.as_view(), name='api_admin_users'),
    path('users/<int:pk>/', AdminUserDetailAPIView.as_view(), name='api_admin_user_detail'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='api_toggle_user_status'),
    path('users/<int:user_id>/financial-logs/', admin_user_financial_logs, name='api_admin_user_financial_logs'),
    path('users/bulk-action/', bulk_user_action, name='api_bulk_user_action'),
    path('users/export/', export_users, name='api_export_users'),
    
    # Posts
    path('posts/', AdminPostListAPIView.as_view(), name='api_admin_posts'),
    path('posts/<int:pk>/', AdminPostDetailAPIView.as_view(), name='api_admin_post_detail'),
    
    # Courses
    path('courses/', AdminCourseListAPIView.as_view(), name='api_admin_courses'),
    path('courses/<int:pk>/', AdminCourseDetailAPIView.as_view(), name='api_admin_course_detail'),
    path('courses/bulk-action/', bulk_course_action, name='api_bulk_course_action'),
    
    # Course Comments
    path('courses/comments/', AdminCourseCommentListAPIView.as_view(), name='api_admin_course_comments'),
    path('courses/comments/<int:pk>/', AdminCourseCommentDetailAPIView.as_view(), name='api_admin_course_comment_detail'),
    path('courses/comments/bulk-action/', bulk_course_comment_action, name='api_bulk_course_comment_action'),
    
    # Sessions - commented out due to therapy_sessions app deletion
    # path('sessions/', AdminSessionListAPIView.as_view(), name='api_admin_sessions'),
    
    # Activities and Notifications
    path('activities/', AdminActivityListAPIView.as_view(), name='api_admin_activities'),
    path('notifications/', AdminNotificationListAPIView.as_view(), name='api_admin_notifications'),
    path('notifications/count/', admin_notification_count, name='api_admin_notification_count'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='api_mark_notification_read'),
    path('notifications/<int:notification_id>/unread/', mark_notification_unread, name='api_mark_notification_unread'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='api_mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', delete_notification, name='api_delete_notification'),
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
    
    # Workshop Registrations
    path('workshops/<int:workshop_id>/registrations/', AdminWorkshopRegistrationListAPIView.as_view(), name='api_admin_workshop_registrations'),
    path('workshops/registrations/<int:registration_id>/approve/', approve_workshop_registration, name='api_approve_workshop_registration'),
    path('workshops/registrations/<int:registration_id>/reject/', reject_workshop_registration, name='api_reject_workshop_registration'),
    
    # Workshop Categories
    path('workshops/categories/', AdminWorkshopCategoryListAPIView.as_view(), name='api_admin_workshop_categories'),
    path('workshops/categories/<int:pk>/', AdminWorkshopCategoryDetailAPIView.as_view(), name='api_admin_workshop_category_detail'),
    
    # Workshop Reviews
    path('workshops/reviews/', AdminWorkshopReviewListAPIView.as_view(), name='api_admin_workshop_reviews'),
    path('workshops/reviews/<int:pk>/', AdminWorkshopReviewDetailAPIView.as_view(), name='api_admin_workshop_review_detail'),
    path('workshops/reviews/bulk-action/', bulk_workshop_review_action, name='api_bulk_workshop_review_action'),
    
    # Package Management
    path('packages/', AdminPackageListAPIView.as_view(), name='api_admin_packages'),
    path('packages/<int:pk>/', AdminPackageDetailAPIView.as_view(), name='api_admin_package_detail'),
    path('packages/bulk-action/', bulk_package_action, name='api_bulk_package_action'),
    path('packages/categories/', AdminPackageCategoryListAPIView.as_view(), name='api_admin_package_categories'),
    path('packages/categories/<int:pk>/', AdminPackageCategoryDetailAPIView.as_view(), name='api_admin_package_category_detail'),
    
    # Package Comments
    path('packages/comments/', AdminPackageCommentListAPIView.as_view(), name='api_admin_package_comments'),
    path('packages/comments/<int:pk>/', AdminPackageCommentDetailAPIView.as_view(), name='api_admin_package_comment_detail'),
    path('packages/comments/bulk-action/', bulk_package_comment_action, name='api_bulk_package_comment_action'),
    
    # File Upload
    path('upload/', upload_file, name='api_upload_file'),
]
