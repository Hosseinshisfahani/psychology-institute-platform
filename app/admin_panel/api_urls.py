from django.urls import path
from .api_views import (
    DashboardStatsAPIView, AdminUserListAPIView, AdminUserDetailAPIView,
    AdminPostListAPIView, AdminPostDetailAPIView, AdminCourseListAPIView,
    AdminCourseDetailAPIView, AdminSessionListAPIView, AdminActivityListAPIView,
    AdminNotificationListAPIView, toggle_user_status, bulk_user_action,
    admin_analytics, send_notification, export_users, bulk_course_action,
    # Old therapy sessions appointments - will be replaced
    # AdminAppointmentListAPIView, AdminAppointmentDetailAPIView, confirm_appointment,
    # reject_appointment, AdminTherapistListAPIView, AdminTherapistDetailAPIView,
    # AdminSessionTypeListAPIView, AdminSessionTypeDetailAPIView,
    AdminBlogPostListAPIView, AdminBlogPostDetailAPIView, bulk_blog_post_action,
    AdminBlogCategoryListAPIView, AdminBlogCategoryDetailAPIView,
    AdminBlogTagListAPIView, AdminBlogTagDetailAPIView,
    AdminBlogCommentListAPIView, AdminBlogCommentDetailAPIView, bulk_blog_comment_action,
    AdminWorkshopListAPIView, AdminWorkshopDetailAPIView, AdminWorkshopSessionListAPIView,
    AdminWorkshopSessionDetailAPIView, AdminWorkshopRegistrationListAPIView,
    bulk_workshop_action, generate_croom_meeting_link, approve_workshop_registration,
    reject_workshop_registration
)

# Import new appointments views
from app.appointments.api_views import (
    AdminAppointmentListAPIView as NewAdminAppointmentListAPIView,
    AdminAppointmentDetailAPIView as NewAdminAppointmentDetailAPIView,
    confirm_appointment as new_confirm_appointment,
    reject_appointment as new_reject_appointment,
    AdminStaffListAPIView, AdminStaffDetailAPIView,
    AdminRoomListAPIView, AdminRoomDetailAPIView,
    AdminAppointmentTypeListAPIView, AdminAppointmentTypeDetailAPIView,
    AdminTimeSlotListAPIView, AdminTimeSlotDetailAPIView
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
    path('users/export/', export_users, name='api_export_users'),
    
    # Posts
    path('posts/', AdminPostListAPIView.as_view(), name='api_admin_posts'),
    path('posts/<int:pk>/', AdminPostDetailAPIView.as_view(), name='api_admin_post_detail'),
    
    # Courses
    path('courses/', AdminCourseListAPIView.as_view(), name='api_admin_courses'),
    path('courses/<int:pk>/', AdminCourseDetailAPIView.as_view(), name='api_admin_course_detail'),
    path('courses/bulk-action/', bulk_course_action, name='api_bulk_course_action'),
    
    # Sessions
    path('sessions/', AdminSessionListAPIView.as_view(), name='api_admin_sessions'),
    
    # Activities and Notifications
    path('activities/', AdminActivityListAPIView.as_view(), name='api_admin_activities'),
    path('notifications/', AdminNotificationListAPIView.as_view(), name='api_admin_notifications'),
    path('notifications/send/', send_notification, name='api_send_notification'),
    
    # Old Therapy Sessions Appointment Management - Commented out
    # path('appointments/', AdminAppointmentListAPIView.as_view(), name='api_admin_appointments'),
    # path('appointments/<int:pk>/', AdminAppointmentDetailAPIView.as_view(), name='api_admin_appointment_detail'),
    # path('appointments/<int:appointment_id>/confirm/', confirm_appointment, name='api_confirm_appointment'),
    # path('appointments/<int:appointment_id>/reject/', reject_appointment, name='api_reject_appointment'),
    
    # New In-Person Appointment Management
    path('in-person-appointments/', NewAdminAppointmentListAPIView.as_view(), name='api_admin_in_person_appointments'),
    path('in-person-appointments/<int:pk>/', NewAdminAppointmentDetailAPIView.as_view(), name='api_admin_in_person_appointment_detail'),
    path('in-person-appointments/<int:appointment_id>/confirm/', new_confirm_appointment, name='api_confirm_in_person_appointment'),
    path('in-person-appointments/<int:appointment_id>/reject/', new_reject_appointment, name='api_reject_in_person_appointment'),
    
    # Staff Management (for in-person appointments)
    path('appointment-staff/', AdminStaffListAPIView.as_view(), name='api_admin_appointment_staff'),
    path('appointment-staff/<int:pk>/', AdminStaffDetailAPIView.as_view(), name='api_admin_appointment_staff_detail'),
    
    # Room Management
    path('rooms/', AdminRoomListAPIView.as_view(), name='api_admin_rooms'),
    path('rooms/<int:pk>/', AdminRoomDetailAPIView.as_view(), name='api_admin_room_detail'),
    
    # Appointment Types Management
    path('appointment-types/', AdminAppointmentTypeListAPIView.as_view(), name='api_admin_appointment_types'),
    path('appointment-types/<int:pk>/', AdminAppointmentTypeDetailAPIView.as_view(), name='api_admin_appointment_type_detail'),
    
    # Time Slots Management
    path('time-slots/', AdminTimeSlotListAPIView.as_view(), name='api_admin_time_slots'),
    path('time-slots/<int:pk>/', AdminTimeSlotDetailAPIView.as_view(), name='api_admin_time_slot_detail'),
    
    # Old Therapist Management - Commented out
    # path('therapists/', AdminTherapistListAPIView.as_view(), name='api_admin_therapists'),
    # path('therapists/<int:pk>/', AdminTherapistDetailAPIView.as_view(), name='api_admin_therapist_detail'),
    
    # Old Session Types Management - Commented out
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
]
