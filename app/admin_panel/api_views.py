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
from app.appointments.models import (
    Staff, AppointmentRoom, AppointmentType, StaffAvailability,
    TimeSlot, Appointment, AppointmentCancellation, AppointmentReminder,
    AppointmentFeedback
)
from app.dashboard.models import Activity, Notification
from app.workshops.models import (
    Workshop, WorkshopCategory, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview
)
from .serializers import (
    AdminUserSerializer, AdminPostSerializer, AdminCourseSerializer,
    AdminActivitySerializer, AdminNotificationSerializer,
    DashboardStatsSerializer, AdminAppointmentSerializer, AdminStaffSerializer,
    AdminAppointmentTypeSerializer, AdminAppointmentRoomSerializer,
    AdminBlogPostSerializer, AdminCategorySerializer,
    AdminTagSerializer, AdminCommentSerializer, AdminWorkshopSerializer,
    AdminWorkshopCategorySerializer, AdminWorkshopSessionSerializer,
    AdminWorkshopRegistrationSerializer
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
        
        # Appointment statistics
        total_appointments = Appointment.objects.count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
        
        # Calculate average appointment rating
        avg_rating = AppointmentFeedback.objects.aggregate(
            avg_rating=Avg('overall_rating')
        )['avg_rating'] or 0
        
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
            'total_appointments': total_appointments,
            'total_revenue': total_revenue,
            'active_users': active_users,
            'pending_appointments': pending_appointments,
            'confirmed_appointments': confirmed_appointments,
            'new_users_this_month': new_users_this_month,
            'completed_appointments': completed_appointments,
            'average_appointment_rating': round(avg_rating, 1),
            'monthly_revenue': monthly_revenue,
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

class AdminUserListAPIView(generics.ListAPIView):
    """
    List all users for admin
    """
    serializer_class = AdminUserSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

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

# AdminSessionListAPIView removed - replaced by AdminAppointmentListAPIView for in-person appointments

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
    
    # Session completion rates
    total_sessions = Session.objects.count()
    completed_sessions = Session.objects.filter(status='completed').count()
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
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

class AdminAppointmentListAPIView(generics.ListAPIView):
    """
    List all appointments for admin
    """
    serializer_class = AdminAppointmentSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'staff', 'appointment_type', 'is_paid']
    search_fields = ['client__first_name', 'client__last_name', 'client__email', 'staff__user__first_name', 'staff__user__last_name', 'phone_number']
    ordering_fields = ['created_at', 'date', 'start_time']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Appointment.objects.all().select_related(
            'client', 'staff__user', 'appointment_type', 'room'
        )

class AdminAppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete an appointment
    """
    serializer_class = AdminAppointmentSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Appointment.objects.all().select_related(
            'client', 'staff__user', 'appointment_type', 'room'
        )

@api_view(['POST'])
@permission_classes([AdminPermission])
def confirm_appointment(request, appointment_id):
    """
    Confirm an appointment
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'pending':
        return Response(
            {'error': 'این وقت ملاقات قبلاً تایید یا لغو شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Assign room if provided
    room_id = request.data.get('room_id')
    if room_id:
        try:
            room = AppointmentRoom.objects.get(id=room_id, is_available=True)
            appointment.room = room
        except AppointmentRoom.DoesNotExist:
            return Response(
                {'error': 'اتاق انتخاب شده یافت نشد یا در دسترس نیست'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Add internal notes if provided
    internal_notes = request.data.get('internal_notes', '')
    if internal_notes:
        appointment.internal_notes = internal_notes
    
    # Confirm the appointment
    appointment.confirm(request.user)
    
    return Response({
        'message': 'وقت ملاقات با موفقیت تایید شد',
        'appointment_id': appointment.id,
        'room': appointment.room.name if appointment.room else None
    })

@api_view(['POST'])
@permission_classes([AdminPermission])
def reject_appointment(request, appointment_id):
    """
    Reject/Cancel an appointment
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status in ['completed', 'cancelled']:
        return Response(
            {'error': 'این وقت ملاقات قبلاً انجام شده یا لغو شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rejection_reason = request.data.get('rejection_reason', '')
    
    # Cancel the appointment
    appointment.cancel(rejection_reason)
    
    # Create cancellation record
    AppointmentCancellation.objects.create(
        appointment=appointment,
        cancelled_by=request.user,
        reason='staff_request',
        explanation=rejection_reason
    )
    
    return Response({
        'message': 'وقت ملاقات لغو شد'
    })

class AdminStaffListAPIView(generics.ListCreateAPIView):
    """
    List and create staff members for admin
    """
    serializer_class = AdminStaffSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_available', 'accepts_appointments']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'bio', 'specializations']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Staff.objects.all().select_related('user')

class AdminStaffDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a staff member
    """
    serializer_class = AdminStaffSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Staff.objects.all().select_related('user')

class AdminAppointmentTypeListAPIView(generics.ListCreateAPIView):
    """
    List and create appointment types for admin
    """
    serializer_class = AdminAppointmentTypeSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'requires_preparation']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'duration_minutes', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return AppointmentType.objects.all()

class AdminAppointmentTypeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete an appointment type
    """
    serializer_class = AdminAppointmentTypeSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return AppointmentType.objects.all()

class AdminAppointmentRoomListAPIView(generics.ListCreateAPIView):
    """
    List and create appointment rooms for admin
    """
    serializer_class = AdminAppointmentRoomSerializer
    permission_classes = [AdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['floor', 'is_available']
    search_fields = ['name', 'room_number', 'facilities']
    ordering_fields = ['floor', 'room_number', 'capacity']
    ordering = ['floor', 'room_number']
    
    def get_queryset(self):
        return AppointmentRoom.objects.all()

class AdminAppointmentRoomDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete an appointment room
    """
    serializer_class = AdminAppointmentRoomSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return AppointmentRoom.objects.all()


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
def generate_croom_meeting_link(request, session_id):
    """
    Generate Croom meeting link for a session
    """
    session = get_object_or_404(WorkshopSession, id=session_id)
    
    try:
        from app.workshops.services.croom_service import croom_service
        
        # Generate meeting link using the existing service
        meeting_data = croom_service.create_meeting(
            title=f"{session.workshop.title} - Session {session.session_number}",
            description=session.description or '',
            start_time=session.scheduled_datetime,
            duration_minutes=session.duration_minutes
        )
        
        if meeting_data:
            session.meeting_link = meeting_data.get('meeting_url')
            session.meeting_id = meeting_data.get('meeting_id')
            session.meeting_password = meeting_data.get('password')
            session.save()
            
            return Response({
                'message': 'لینک جلسه با موفقیت تولید شد',
                'meeting_link': session.meeting_link,
                'meeting_id': session.meeting_id
            })
        else:
            return Response(
                {'error': 'خطا در تولید لینک جلسه'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        return Response(
            {'error': f'خطا در تولید لینک جلسه: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
