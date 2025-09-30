from rest_framework import generics, views, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from blog.models import Post, Category
from courses.models import Course, Enrollment
from therapy_sessions.models import Session, Therapist
from dashboard.models import Activity, Notification
from .serializers import (
    AdminUserSerializer, AdminPostSerializer, AdminCourseSerializer,
    AdminSessionSerializer, AdminActivitySerializer, AdminNotificationSerializer,
    DashboardStatsSerializer
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
        
        # Session statistics
        total_sessions = Session.objects.count()
        completed_sessions = Session.objects.filter(status='completed').count()
        pending_sessions = Session.objects.filter(status='scheduled').count()
        
        # Calculate average session rating
        avg_rating = Session.objects.filter(
            status='completed',
            rating__isnull=False
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
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

class AdminSessionListAPIView(generics.ListAPIView):
    """
    List all sessions for admin
    """
    serializer_class = AdminSessionSerializer
    permission_classes = [AdminPermission]
    
    def get_queryset(self):
        return Session.objects.all().select_related('user', 'therapist__user', 'session_type').order_by('-created_at')

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
