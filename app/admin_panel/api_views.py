from rest_framework import generics, views, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from app.blog.models import Post, Category, Tag, Comment
from app.courses.models import Course, Enrollment
# from app.therapy_sessions.models import Session, Therapist, SessionBooking, SessionType  # Removed - therapy_sessions app deleted
from app.dashboard.models import Activity, Notification
from app.workshops.models import (
    Workshop, WorkshopCategory, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview
)
from app.packages.models import Package, PackageCategory, PackagePurchase
from .serializers import (
    AdminUserSerializer, AdminPostSerializer, AdminCourseSerializer,
    # AdminSessionSerializer, AdminAppointmentSerializer, AdminTherapistSerializer, AdminSessionTypeSerializer,  # Removed - therapy_sessions app deleted
    AdminActivitySerializer, AdminNotificationSerializer,
    DashboardStatsSerializer, AdminBlogPostSerializer, AdminCategorySerializer,
    AdminTagSerializer, AdminCommentSerializer, AdminWorkshopSerializer,
    AdminWorkshopCategorySerializer, AdminWorkshopSessionSerializer,
    AdminWorkshopRegistrationSerializer, AdminPackageSerializer, AdminPackageCategorySerializer
)

User = get_user_model()

class AdminPermission(permissions.BasePermission):
    """
    Custom permission to only allow admin users
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'admin'

class DashboardStatsAPIView(views.APIView):
    """
    Get dashboard statistics for admin panel
    """
    permission_classes = [AdminPermission]

    def get(self, request):
        # Calculate date ranges
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__gte=now - timedelta(days=30)).count()
        new_users_this_month = User.objects.filter(date_joined__gte=this_month_start).count()
        
        # Course statistics
        total_courses = Course.objects.count()
        

        total_sessions = 0
        completed_sessions = 0
        pending_sessions = 0
        
        # Calculate average session rating - commented out due to therapy_sessions app deletion
        # avg_rating = Session.objects.filter(
        #     status='completed',
        #     rating__isnull=False
        # ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        avg_rating = 0
        
        # Revenue calculations
        total_revenue = Enrollment.objects.aggregate(
            total=Sum('course__price')
        )['total'] or 0
        
        monthly_revenue = Enrollment.objects.filter(
            enrolled_at__gte=this_month_start
        ).aggregate(
            total=Sum('course__price')
        )['total'] or 0
        
        stats = {
            'total_users': total_users,
            'total_courses': total_courses,
            'total_sessions': total_sessions,
            'total_revenue': total_revenue,
            'active_users': active_users,
            'pending_sessions': pending_sessions,
            'new_users_this_month': new_users_this_month,
            'completed_sessions': completed_sessions,
            'average_session_rating': round(avg_rating, 1),
            'monthly_revenue': monthly_revenue,
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

class AdminUserListAPIView(generics.ListAPIView):
    """
    List all users for admin with pagination, filtering, and search
    """
    serializer_class = AdminUserSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_type', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['date_joined', 'last_login', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        # Additional filtering based on query parameters
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset

class AdminUserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a user
    """
    serializer_class = AdminUserSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return User.objects.all()

class AdminPostListAPIView(generics.ListCreateAPIView):
    """
    List and create posts for admin
    """
    serializer_class = AdminPostSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Post.objects.all().select_related('author', 'category').order_by('-created_at')

class AdminPostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a post
    """
    serializer_class = AdminPostSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Post.objects.all()

class AdminCourseListAPIView(generics.ListCreateAPIView):
    """
    List and create courses for admin
    """
    serializer_class = AdminCourseSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Course.objects.all().select_related('instructor').order_by('-created_at')

class AdminCourseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a course
    """
    serializer_class = AdminCourseSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Course.objects.all()

# AdminSessionListAPIView commented out due to therapy_sessions app deletion
# class AdminSessionListAPIView(generics.ListAPIView):
#     """
#     List all sessions for admin
#     """
#     serializer_class = AdminSessionSerializer
#     permission_classes = [AdminPermission]
#     
#     def get_queryset(self):
#         return Session.objects.all().select_related('user', 'therapist__user', 'session_type').order_by('-created_at')

class AdminActivityListAPIView(generics.ListAPIView):
    """
    List recent activities for admin
    """
    serializer_class = AdminActivitySerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Activity.objects.all().select_related('user').order_by('-created_at')[:50]

class AdminNotificationListAPIView(generics.ListAPIView):
    """
    List all notifications for admin
    """
    serializer_class = AdminNotificationSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Notification.objects.all().select_related('user').order_by('-created_at')

@api_view(['POST'])
@permission_classes([AdminPermission])
def toggle_user_status(request, user_id):
    """
    Toggle user active status
    """
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    return Response({
        'message': f'کاربر {"فعال" if user.is_active else "غیرفعال"} شد',
        'is_active': user.is_active
    })

@api_view(['POST'])
@permission_classes([AdminPermission])
def bulk_user_action(request):
    """
    Perform bulk actions on users
    """
    action = request.data.get('action')
    user_ids = request.data.get('user_ids', [])
    
    if not user_ids:
        return Response({'error': 'هیچ کاربری انتخاب نشده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    users = User.objects.filter(id__in=user_ids)
    
    if action == 'activate':
        users.update(is_active=True)
        message = f'{users.count()} کاربر فعال شدند'
    elif action == 'deactivate':
        users.update(is_active=False)
        message = f'{users.count()} کاربر غیرفعال شدند'
    elif action == 'delete':
        users.delete()
        message = f'{len(user_ids)} کاربر حذف شدند'
    else:
        return Response({'error': 'عملیات نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message})

@api_view(['GET'])
@permission_classes([AdminPermission])
def admin_analytics(request):
    """
    Get analytics data for admin dashboard
    """
    # User registration trends (last 12 months)
    user_trends = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = User.objects.filter(date_joined__range=[month_start, month_end]).count()
        user_trends.append({
            'month': month_start.strftime('%Y/%m'),
            'count': count
        })
    
    # Course enrollment trends
    course_trends = []
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = Enrollment.objects.filter(enrolled_at__range=[month_start, month_end]).count()
        course_trends.append({
            'month': month_start.strftime('%Y/%m'),
            'count': count
        })
    
    # Top performing courses
    top_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]
    
    # Session completion rates - commented out due to therapy_sessions app deletion
    # total_sessions = Session.objects.count()
    # completed_sessions = Session.objects.filter(status='completed').count()
    # completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    total_sessions = 0
    completed_sessions = 0
    completion_rate = 0
    
    return Response({
        'user_trends': user_trends,
        'course_trends': course_trends,
        'top_courses': [
            {
                'title': course.title,
                'enrollment_count': course.enrollment_count
            }
            for course in top_courses
        ],
        'completion_rate': round(completion_rate, 1)
    })

@api_view(['POST'])
@permission_classes([AdminPermission])
def send_notification(request):
    """
    Send notification to users
    """
    title = request.data.get('title')
    message = request.data.get('message')
    notification_type = request.data.get('type', 'info')
    target_users = request.data.get('target_users', 'all')
    
    if not title or not message:
        return Response({'error': 'عنوان و پیام الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Determine target users
    if target_users == 'all':
        users = User.objects.filter(is_active=True)
    elif target_users == 'students':
        users = User.objects.filter(user_type='student', is_active=True)
    elif target_users == 'therapists':
        users = User.objects.filter(user_type='therapist', is_active=True)
    else:
        return Response({'error': 'نوع کاربران نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create notifications
    notifications = []
    for user in users:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type
        )
        notifications.append(notification)
    
    return Response({
        'message': f'{len(notifications)} اعلان ارسال شد',
        'count': len(notifications)
    })

@api_view(['GET'])
@permission_classes([AdminPermission])
def export_users(request):
    """
    Export users to CSV
    """
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    response.write('\ufeff')  # UTF-8 BOM for Excel
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Email', 'First Name', 'Last Name', 'User Type', 'Is Active', 'Date Joined', 'Last Login'])
    
    users = User.objects.all().order_by('-date_joined')
    for user in users:
        writer.writerow([
            user.id,
            user.email,
            user.first_name or '',
            user.last_name or '',
            user.user_type,
            'Yes' if user.is_active else 'No',
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
        ])
    
    return response

@api_view(['POST'])
@permission_classes([AdminPermission])
def bulk_course_action(request):
    """
    Perform bulk actions on courses
    """
    action = request.data.get('action')
    course_ids = request.data.get('course_ids', [])
    
    if not course_ids:
        return Response({'error': 'هیچ بسته آموزشی‌ای انتخاب نشده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    courses = Course.objects.filter(id__in=course_ids)
    
    if action == 'publish':
        courses.update(status='published')
        message = f'{courses.count()} بسته آموزشی منتشر شدند'
    elif action == 'archive':
        courses.update(status='archived')
        message = f'{courses.count()} بسته آموزشی بایگانی شدند'
    elif action == 'delete':
        count = courses.count()
        courses.delete()
        message = f'{count} بسته آموزشی حذف شدند'
    else:
        return Response({'error': 'عملیات نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message})


# Appointment Management Endpoints

# AdminAppointmentListAPIView commented out due to therapy_sessions app deletion
# class AdminAppointmentListAPIView(generics.ListAPIView):
#     """
#     List all appointment bookings for admin
#     """
#     serializer_class = AdminAppointmentSerializer
#     permission_classes = [AdminPermission]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['status', 'mode', 'therapist', 'session_type']
#     search_fields = ['user__first_name', 'user__last_name', 'user__email', 'therapist__user__first_name', 'therapist__user__last_name']
#     ordering_fields = ['created_at', 'preferred_date', 'preferred_time']
#     ordering = ['-created_at']
#     
#     def get_queryset(self):
#         return SessionBooking.objects.all().select_related(
#             'user', 'therapist__user', 'session_type'
#         )

# AdminAppointmentDetailAPIView commented out due to therapy_sessions app deletion
# class AdminAppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     Get, update, or delete an appointment booking
#     """
#     serializer_class = AdminAppointmentSerializer
#     permission_classes = [AdminPermission]
#     
#     def get_queryset(self):
#         return SessionBooking.objects.all().select_related(
#             'user', 'therapist__user', 'session_type'
#         )

# confirm_appointment function commented out due to therapy_sessions app deletion
# @api_view(['POST'])
# @permission_classes([AdminPermission])
# def confirm_appointment(request, appointment_id):
#     """
#     Confirm an appointment booking
#     """
#     appointment = get_object_or_404(SessionBooking, id=appointment_id)
#     
#     if appointment.status != 'pending':
#         return Response(
#             {'error': 'این نوبت قبلاً تایید یا رد شده است'}, 
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     
#     confirmed_date = request.data.get('confirmed_date')
#     confirmed_time = request.data.get('confirmed_time')
#     croom_class_url = request.data.get('croom_class_url', '')
#     croom_meeting_id = request.data.get('croom_meeting_id', '')
#     croom_password = request.data.get('croom_password', '')
#     confirmation_notes = request.data.get('confirmation_notes', '')
#     
#     if not all([confirmed_date, confirmed_time]):
#         return Response(
#             {'error': 'تاریخ و زمان تایید الزامی است'}, 
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     
#     try:
#         from datetime import datetime
#         confirmed_date_obj = datetime.strptime(confirmed_date, '%Y-%m-%d').date()
#         confirmed_time_obj = datetime.strptime(confirmed_time, '%H:%M').time()
#     except ValueError:
#         return Response(
#             {'error': 'فرمت تاریخ یا زمان نامعتبر است'}, 
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     
#     # Update appointment with croom details
#     appointment.croom_class_url = croom_class_url
#     appointment.croom_meeting_id = croom_meeting_id
#     appointment.croom_password = croom_password
#     
#     # Confirm appointment and create session
#     session = appointment.confirm_booking(
#         confirmed_date_obj,
#         confirmed_time_obj,
#         request.user,
#         confirmation_notes
#     )
#     
#     return Response({
#         'message': 'نوبت با موفقیت تایید شد',
#         'session_id': session.id,
#         'croom_class_url': croom_class_url,
#         'croom_meeting_id': croom_meeting_id
#     })

# reject_appointment function commented out due to therapy_sessions app deletion
# @api_view(['POST'])
# @permission_classes([AdminPermission])
# def reject_appointment(request, appointment_id):
#     """
#     Reject an appointment booking
#     """
#     appointment = get_object_or_404(SessionBooking, id=appointment_id)
#     
#     if appointment.status != 'pending':
#         return Response(
#             {'error': 'این نوبت قبلاً تایید یا رد شده است'}, 
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     
#     rejection_reason = request.data.get('rejection_reason', '')
#     
#     appointment.status = 'rejected'
#     appointment.confirmation_notes = rejection_reason
#     appointment.save()
#     
#     return Response({
#         'message': 'نوبت رد شد'
#     })

# AdminTherapistListAPIView commented out due to therapy_sessions app deletion
# class AdminTherapistListAPIView(generics.ListCreateAPIView):
#     """
#     List and create therapists for admin
#     """
#     serializer_class = AdminTherapistSerializer
#     permission_classes = [AdminPermission]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['specialization', 'is_available']
#     search_fields = ['user__first_name', 'user__last_name', 'user__email', 'bio']
#     ordering_fields = ['hourly_rate', 'created_at']
#     ordering = ['-created_at']
#     
#     def get_queryset(self):
#         return Therapist.objects.all().select_related('user')

# AdminTherapistDetailAPIView commented out due to therapy_sessions app deletion
# class AdminTherapistDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     Get, update, or delete a therapist
#     """
#     serializer_class = AdminTherapistSerializer
#     permission_classes = [AdminPermission]
#     
#     def get_queryset(self):
#         return Therapist.objects.all().select_related('user')

# AdminSessionTypeListAPIView commented out due to therapy_sessions app deletion
# class AdminSessionTypeListAPIView(generics.ListCreateAPIView):
#     """
#     List and create session types for admin
#     """
#     serializer_class = AdminSessionTypeSerializer
#     permission_classes = [AdminPermission]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['is_active']
#     search_fields = ['name', 'description']
#     ordering_fields = ['price', 'duration_minutes', 'created_at']
#     ordering = ['-created_at']
#     
#     def get_queryset(self):
#         return SessionType.objects.all()

# AdminSessionTypeDetailAPIView commented out due to therapy_sessions app deletion
# class AdminSessionTypeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     Get, update, or delete a session type
#     """
#     serializer_class = AdminSessionTypeSerializer
#     permission_classes = [AdminPermission]
#     
#     def get_queryset(self):
#         return SessionType.objects.all()


# Blog Admin Views

class AdminBlogPostListAPIView(generics.ListCreateAPIView):
    """
    List and create blog posts for admin
    """
    serializer_class = AdminBlogPostSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'author', 'is_featured']
    search_fields = ['title', 'content', 'excerpt', 'author__first_name', 'author__last_name']
    ordering_fields = ['created_at', 'updated_at', 'published_at', 'view_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Post.objects.all().select_related('author', 'category').prefetch_related('tags')
        
        # Date range filter
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass
        
        # Tag filter
        tag_ids = self.request.query_params.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids)
        
        return queryset

class AdminBlogPostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a blog post
    """
    serializer_class = AdminBlogPostSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Post.objects.all().select_related('author', 'category').prefetch_related('tags')

@api_view(['POST'])
@permission_classes([AdminPermission])
def bulk_blog_post_action(request):
    """
    Perform bulk actions on blog posts
    """
    action = request.data.get('action')
    post_ids = request.data.get('post_ids', [])
    
    if not post_ids:
        return Response({'error': 'هیچ پستی انتخاب نشده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    posts = Post.objects.filter(id__in=post_ids)
    
    if action == 'publish':
        posts.update(status='published', published_at=timezone.now())
        message = f'{posts.count()} پست منتشر شدند'
    elif action == 'unpublish':
        posts.update(status='draft')
        message = f'{posts.count()} پست به حالت پیش‌نویس برگشتند'
    elif action == 'archive':
        posts.update(status='archived')
        message = f'{posts.count()} پست بایگانی شدند'
    elif action == 'delete':
        count = posts.count()
        posts.delete()
        message = f'{count} پست حذف شدند'
    else:
        return Response({'error': 'عملیات نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message})

class AdminBlogCategoryListAPIView(generics.ListCreateAPIView):
    """
    List and create blog categories for admin
    """
    serializer_class = AdminCategorySerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return Category.objects.all()

class AdminBlogCategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a blog category
    """
    serializer_class = AdminCategorySerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Category.objects.all()

class AdminBlogTagListAPIView(generics.ListCreateAPIView):
    """
    List and create blog tags for admin
    """
    serializer_class = AdminTagSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'usage_count']
    ordering = ['name']
    
    def get_queryset(self):
        return Tag.objects.all()

class AdminBlogTagDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a blog tag
    """
    serializer_class = AdminTagSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Tag.objects.all()

class AdminBlogCommentListAPIView(generics.ListAPIView):
    """
    List blog comments for admin moderation
    """
    serializer_class = AdminCommentSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_approved', 'post']
    search_fields = ['content', 'author__first_name', 'author__last_name', 'author__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Comment.objects.all().select_related('author', 'post')

class AdminBlogCommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a blog comment
    """
    serializer_class = AdminCommentSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Comment.objects.all().select_related('author', 'post')

@api_view(['POST'])
@permission_classes([AdminPermission])
def bulk_blog_comment_action(request):
    """
    Perform bulk actions on blog comments
    """
    action = request.data.get('action')
    comment_ids = request.data.get('comment_ids', [])
    
    if not comment_ids:
        return Response({'error': 'هیچ نظری انتخاب نشده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    comments = Comment.objects.filter(id__in=comment_ids)
    
    if action == 'approve':
        comments.update(is_approved=True)
        message = f'{comments.count()} نظر تایید شدند'
    elif action == 'reject':
        comments.update(is_approved=False)
        message = f'{comments.count()} نظر رد شدند'
    elif action == 'delete':
        count = comments.count()
        comments.delete()
        message = f'{count} نظر حذف شدند'
    else:
        return Response({'error': 'عملیات نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message})


# Workshop Admin Views

class AdminWorkshopListAPIView(generics.ListCreateAPIView):
    """
    List and create workshops for admin
    """
    serializer_class = AdminWorkshopSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'difficulty', 'instructor', 'payment_type']
    search_fields = ['title', 'description', 'short_description', 'instructor__first_name', 'instructor__last_name']
    ordering_fields = ['created_at', 'start_date', 'price', 'current_participants', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Workshop.objects.all().select_related(
            'category', 'instructor'
        ).prefetch_related('sessions', 'registrations')
        
        # Date range filter
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(end_date__lte=date_to_obj)
            except ValueError:
                pass
        
        return queryset

class AdminWorkshopDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a workshop
    """
    serializer_class = AdminWorkshopSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Workshop.objects.all().select_related(
            'category', 'instructor'
        ).prefetch_related('sessions', 'registrations')

class AdminWorkshopSessionListAPIView(generics.ListCreateAPIView):
    """
    List and create sessions for a workshop
    """
    serializer_class = AdminWorkshopSessionSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_completed']
    ordering_fields = ['session_number', 'scheduled_datetime']
    ordering = ['session_number']
    
    def get_queryset(self):
        workshop_id = self.kwargs.get('workshop_id')
        return WorkshopSession.objects.filter(workshop_id=workshop_id)
    
    def perform_create(self, serializer):
        workshop_id = self.kwargs.get('workshop_id')
        workshop = get_object_or_404(Workshop, id=workshop_id)
        serializer.save(workshop=workshop)

class AdminWorkshopSessionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a workshop session
    """
    serializer_class = AdminWorkshopSessionSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        workshop_id = self.kwargs.get('workshop_id')
        return WorkshopSession.objects.filter(workshop_id=workshop_id)

class AdminWorkshopRegistrationListAPIView(generics.ListAPIView):
    """
    List registrations for a workshop
    """
    serializer_class = AdminWorkshopRegistrationSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_type']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['registered_at', 'amount_paid', 'progress_percentage']
    ordering = ['-registered_at']
    
    def get_queryset(self):
        workshop_id = self.kwargs.get('workshop_id')
        return WorkshopRegistration.objects.filter(
            workshop_id=workshop_id
        ).select_related('user', 'workshop')

@api_view(['POST'])
@permission_classes([AdminPermission])
def bulk_workshop_action(request):
    """
    Perform bulk actions on workshops
    """
    action = request.data.get('action')
    workshop_ids = request.data.get('workshop_ids', [])
    
    if not workshop_ids:
        return Response({'error': 'هیچ کارگاهی انتخاب نشده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    workshops = Workshop.objects.filter(id__in=workshop_ids)
    
    if action == 'publish':
        workshops.update(status='published', published_at=timezone.now())
        message = f'{workshops.count()} کارگاه منتشر شدند'
    elif action == 'archive':
        workshops.update(status='archived')
        message = f'{workshops.count()} کارگاه بایگانی شدند'
    elif action == 'open_registration':
        workshops.update(status='registration_open')
        message = f'{workshops.count()} کارگاه برای ثبت‌نام باز شدند'
    elif action == 'close_registration':
        workshops.update(status='published')
        message = f'{workshops.count()} کارگاه از ثبت‌نام بسته شدند'
    elif action == 'delete':
        count = workshops.count()
        workshops.delete()
        message = f'{count} کارگاه حذف شدند'
    else:
        return Response({'error': 'عملیات نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message})


@api_view(['POST'])
@permission_classes([AdminPermission])
def approve_workshop_registration(request, registration_id):
    """
    Approve a workshop registration
    """
    registration = get_object_or_404(WorkshopRegistration, id=registration_id)
    
    if registration.status != 'pending_payment':
        return Response(
            {'error': 'این ثبت‌نام قبلاً تایید یا رد شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    registration.status = 'active'
    registration.save()
    
    return Response({
        'message': 'ثبت‌نام با موفقیت تایید شد',
        'status': registration.status
    })

@api_view(['POST'])
@permission_classes([AdminPermission])
def reject_workshop_registration(request, registration_id):
    """
    Reject a workshop registration
    """
    registration = get_object_or_404(WorkshopRegistration, id=registration_id)
    
    if registration.status != 'pending_payment':
        return Response(
            {'error': 'این ثبت‌نام قبلاً تایید یا رد شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rejection_reason = request.data.get('rejection_reason', '')
    
    registration.status = 'cancelled'
    registration.save()
    
    return Response({
        'message': 'ثبت‌نام رد شد',
        'status': registration.status
    })


# Package Admin Views

class AdminPackageListAPIView(generics.ListCreateAPIView):
    """
    List and create packages for admin
    """
    serializer_class = AdminPackageSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'is_featured']
    search_fields = ['title', 'description', 'short_description']
    ordering_fields = ['created_at', 'updated_at', 'price', 'purchase_count', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Package.objects.all().select_related('category').prefetch_related('courses')
        
        # Date range filter
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass
        
        return queryset

class AdminPackageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a package
    """
    serializer_class = AdminPackageSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Package.objects.all().select_related('category').prefetch_related('courses')

class AdminPackageCategoryListAPIView(generics.ListCreateAPIView):
    """
    List and create package categories for admin
    """
    serializer_class = AdminPackageCategorySerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return PackageCategory.objects.all()

class AdminPackageCategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a package category
    """
    serializer_class = AdminPackageCategorySerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return PackageCategory.objects.all()

@api_view(['POST'])
@permission_classes([AdminPermission])
def bulk_package_action(request):
    """
    Perform bulk actions on packages
    """
    action = request.data.get('action')
    package_ids = request.data.get('package_ids', [])
    
    if not package_ids:
        return Response({'error': 'هیچ پکیجی انتخاب نشده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    packages = Package.objects.filter(id__in=package_ids)
    
    if action == 'publish':
        packages.update(status='published', published_at=timezone.now())
        message = f'{packages.count()} پکیج منتشر شدند'
    elif action == 'archive':
        packages.update(status='archived')
        message = f'{packages.count()} پکیج بایگانی شدند'
    elif action == 'delete':
        count = packages.count()
        packages.delete()
        message = f'{count} پکیج حذف شدند'
    else:
        return Response({'error': 'عملیات نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message})


# Workshop Categories Admin Views

class AdminWorkshopCategoryListAPIView(generics.ListCreateAPIView):
    """
    List and create workshop categories for admin
    """
    serializer_class = AdminWorkshopCategorySerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return WorkshopCategory.objects.all()

class AdminWorkshopCategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a workshop category
    """
    serializer_class = AdminWorkshopCategorySerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return WorkshopCategory.objects.all()
