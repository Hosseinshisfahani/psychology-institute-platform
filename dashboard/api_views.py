from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import User, UserProfile, Notification
from .serializers import (
    UserSerializer, UserProfileSerializer, NotificationSerializer,
    DashboardStatsSerializer, EnrollmentSerializer, TestResultSerializer, SessionSerializer
)
from courses.models import Enrollment
from tests.models import TestResult
from therapy_sessions.models import Session


# Authentication API Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_login(request):
    """API login endpoint that accepts JSON"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'success': False, 'message': 'ایمیل و رمز عبور الزامی است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'success': True,
            'message': f'خوش آمدید {user.full_name}!',
            'user': UserSerializer(user).data
        })
    else:
        return Response(
            {'success': False, 'message': 'ایمیل یا رمز عبور اشتباه است'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_signup(request):
    """API signup endpoint that accepts JSON"""
    email = request.data.get('email')
    password1 = request.data.get('password1')
    password2 = request.data.get('password2')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    
    # Validate required fields
    if not all([email, password1, password2, first_name, last_name]):
        return Response(
            {'success': False, 'message': 'تمام فیلدها الزامی هستند'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate passwords match
    if password1 != password2:
        return Response(
            {'success': False, 'message': 'رمزهای عبور مطابقت ندارند'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {'success': False, 'message': 'کاربری با این ایمیل قبلاً ثبت‌نام کرده است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    try:
        user = User.objects.create_user(
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            user_type='client'
        )
        
        # Log the user in
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return Response({
            'success': True,
            'message': f'حساب کاربری شما با موفقیت ایجاد شد! خوش آمدید {user.full_name}',
            'user': UserSerializer(user).data
        })
    except Exception as e:
        return Response(
            {'success': False, 'message': f'خطا در ایجاد حساب کاربری: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_logout(request):
    """API logout endpoint"""
    logout(request)
    return Response({'success': True, 'message': 'با موفقیت خارج شدید'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the user"""
    user = request.user
    
    # Get counts
    enrolled_courses_count = Enrollment.objects.filter(user=user).count()
    completed_tests_count = TestResult.objects.filter(session__user=user).count()
    upcoming_sessions_count = Session.objects.filter(
        client=user, 
        scheduled_date__gte=timezone.now(),
        status='scheduled'
    ).count()
    certificates_count = Enrollment.objects.filter(
        user=user, 
        status='completed'
    ).count()
    unread_notifications_count = Notification.objects.filter(
        user=user, 
        is_read=False
    ).count()
    
    stats = {
        'enrolled_courses_count': enrolled_courses_count,
        'completed_tests_count': completed_tests_count,
        'upcoming_sessions_count': upcoming_sessions_count,
        'certificates_count': certificates_count,
        'unread_notifications_count': unread_notifications_count
    }
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_enrollments(request):
    """Get user's course enrollments"""
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrolled_at')
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_test_results(request):
    """Get user's test results"""
    test_results = TestResult.objects.filter(session__user=request.user).select_related('session__test').order_by('-generated_at')
    serializer = TestResultSerializer(test_results, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_sessions(request):
    """Get user's therapy sessions"""
    sessions = Session.objects.filter(client=request.user).select_related('therapist').order_by('-scheduled_date')
    serializer = SessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'message': 'Notification marked as read'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_activities(request):
    """Get user's recent activities"""
    activities = []
    
    # Recent enrollments
    recent_enrollments = Enrollment.objects.filter(user=request.user).order_by('-enrolled_at')[:5]
    for enrollment in recent_enrollments:
        activities.append({
            'type': 'enrollment',
            'title': f'ثبت‌نام در دوره {enrollment.course.title}',
            'description': f'شما در دوره {enrollment.course.title} ثبت‌نام کردید',
            'created_at': enrollment.enrolled_at,
            'created_at_persian': enrollment.enrolled_at.strftime('%Y/%m/%d') if enrollment.enrolled_at else None
        })
    
    # Recent test results
    recent_tests = TestResult.objects.filter(session__user=request.user).select_related('session__test').order_by('-generated_at')[:5]
    for test_result in recent_tests:
        activities.append({
            'type': 'test_result',
            'title': f'تکمیل تست {test_result.session.test.title}',
            'description': f'نتیجه تست: {test_result.percentage:.1f}%',
            'created_at': test_result.generated_at,
            'created_at_persian': test_result.generated_at.strftime('%Y/%m/%d') if test_result.generated_at else None
        })
    
    # Recent sessions
    recent_sessions = Session.objects.filter(client=request.user).select_related('therapist').order_by('-scheduled_date')[:5]
    for session in recent_sessions:
        activities.append({
            'type': 'session',
            'title': f'جلسه با {session.therapist.user.get_full_name()}',
            'description': f'جلسه {session.get_mode_display()}',
            'created_at': session.scheduled_date,
            'created_at_persian': session.scheduled_date.strftime('%Y/%m/%d') if session.scheduled_date else None
        })
    
    # Sort by date and return latest 10
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    return Response(activities[:10])
