from rest_framework import serializers
from .models import User, UserProfile, Notification
from courses.models import Enrollment
from tests.models import TestResult
from therapy_sessions.models import Session


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'phone_number', 'date_of_birth', 'gender', 'address',
            'city', 'postal_code', 'bio', 'profile_image', 'created_at', 'updated_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'is_active', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class NotificationSerializer(serializers.ModelSerializer):
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'type', 'is_read', 'created_at', 'created_at_persian'
        ]
    
    def get_created_at_persian(self, obj):
        from django.utils import timezone
        import jdatetime
        if obj.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jalali_date.strftime('%Y/%m/%d')
        return None


class DashboardStatsSerializer(serializers.Serializer):
    enrolled_courses_count = serializers.IntegerField()
    completed_tests_count = serializers.IntegerField()
    upcoming_sessions_count = serializers.IntegerField()
    certificates_count = serializers.IntegerField()
    unread_notifications_count = serializers.IntegerField()


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    enrollment_date_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'course_slug', 'enrollment_date',
            'enrollment_date_persian', 'is_completed', 'progress_percentage'
        ]
    
    def get_enrollment_date_persian(self, obj):
        from django.utils import timezone
        import jdatetime
        if obj.enrollment_date:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.enrollment_date)
            return jalali_date.strftime('%Y/%m/%d')
        return None


class TestResultSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    test_slug = serializers.CharField(source='test.slug', read_only=True)
    completed_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'test', 'test_title', 'test_slug', 'score', 'total_questions',
            'correct_answers', 'completed_at', 'completed_at_persian', 'result_data'
        ]
    
    def get_completed_at_persian(self, obj):
        from django.utils import timezone
        import jdatetime
        if obj.completed_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.completed_at)
            return jalali_date.strftime('%Y/%m/%d')
        return None


class SessionSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source='therapist.full_name', read_only=True)
    session_date_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = [
            'id', 'therapist', 'therapist_name', 'session_type', 'scheduled_date',
            'session_date_persian', 'duration', 'status', 'notes', 'rating'
        ]
    
    def get_session_date_persian(self, obj):
        from django.utils import timezone
        import jdatetime
        if obj.scheduled_date:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.scheduled_date)
            return jalali_date.strftime('%Y/%m/%d')
        return None
