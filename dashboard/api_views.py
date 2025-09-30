from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from .models import User, UserProfile, Notification
from .serializers import (
    UserSerializer, UserProfileSerializer, NotificationSerializer,
    DashboardStatsSerializer, EnrollmentSerializer, TestResultSerializer, SessionSerializer
)
from courses.models import Enrollment
from tests.models import TestResult
from therapy_sessions.models import Session


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
    completed_tests_count = TestResult.objects.filter(user=user).count()
    upcoming_sessions_count = Session.objects.filter(
        user=user, 
        scheduled_date__gte=timezone.now(),
        status='scheduled'
    ).count()
    certificates_count = Enrollment.objects.filter(
        user=user, 
        is_completed=True
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
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course').order_by('-enrollment_date')
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_test_results(request):
    """Get user's test results"""
    test_results = TestResult.objects.filter(user=request.user).select_related('test').order_by('-completed_at')
    serializer = TestResultSerializer(test_results, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_sessions(request):
    """Get user's therapy sessions"""
    sessions = Session.objects.filter(user=request.user).select_related('therapist').order_by('-scheduled_date')
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
    recent_enrollments = Enrollment.objects.filter(user=request.user).order_by('-enrollment_date')[:5]
    for enrollment in recent_enrollments:
        activities.append({
            'type': 'enrollment',
            'title': f'ثبت‌نام در دوره {enrollment.course.title}',
            'description': f'شما در دوره {enrollment.course.title} ثبت‌نام کردید',
            'created_at': enrollment.enrollment_date,
            'created_at_persian': enrollment.enrollment_date.strftime('%Y/%m/%d') if enrollment.enrollment_date else None
        })
    
    # Recent test results
    recent_tests = TestResult.objects.filter(user=request.user).order_by('-completed_at')[:5]
    for test_result in recent_tests:
        activities.append({
            'type': 'test_result',
            'title': f'تکمیل تست {test_result.test.title}',
            'description': f'نتیجه تست: {test_result.score} از {test_result.total_questions}',
            'created_at': test_result.completed_at,
            'created_at_persian': test_result.completed_at.strftime('%Y/%m/%d') if test_result.completed_at else None
        })
    
    # Recent sessions
    recent_sessions = Session.objects.filter(user=request.user).order_by('-scheduled_date')[:5]
    for session in recent_sessions:
        activities.append({
            'type': 'session',
            'title': f'جلسه با {session.therapist.full_name}',
            'description': f'جلسه {session.get_session_type_display()}',
            'created_at': session.scheduled_date,
            'created_at_persian': session.scheduled_date.strftime('%Y/%m/%d') if session.scheduled_date else None
        })
    
    # Sort by date and return latest 10
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    return Response(activities[:10])
