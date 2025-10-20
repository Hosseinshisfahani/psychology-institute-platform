from rest_framework import serializers
from .models import User, UserProfile, Notification
from app.courses.models import Enrollment
from app.tests.models import TestResult
# from app.therapy_sessions.models import Session  # Commented out - therapy_sessions app doesn't exist


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'emergency_contact_name', 'emergency_contact_phone', 
            'medical_conditions', 'medications', 'therapy_goals',
            'preferred_language', 'timezone', 'notification_preferences',
            'created_at', 'updated_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'phone_number', 'national_id', 'birth_date', 'gender',
            'address', 'city', 'postal_code', 'profile_image', 'bio',
            'is_active', 'is_verified', 'is_staff', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_verified', 'is_staff']
    
    def to_representation(self, instance):
        """Convert profile_image to full URL in the response"""
        representation = super().to_representation(instance)
        if instance.profile_image:
            request = self.context.get('request')
            if request:
                representation['profile_image'] = request.build_absolute_uri(instance.profile_image.url)
            else:
                representation['profile_image'] = instance.profile_image.url
        return representation


class NotificationSerializer(serializers.ModelSerializer):
    created_at_persian = serializers.SerializerMethodField()
    type = serializers.CharField(source='notification_type', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'type', 'notification_type', 'is_read', 'created_at', 'created_at_persian'
        ]
    
    def get_created_at_persian(self, obj):
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
    enrolled_at_persian = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'course_slug', 'enrolled_at',
            'enrolled_at_persian', 'status', 'is_completed', 'progress_percentage',
            'completed_at', 'last_accessed'
        ]
    
    def get_enrolled_at_persian(self, obj):
        import jdatetime
        if obj.enrolled_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.enrolled_at)
            return jalali_date.strftime('%Y/%m/%d')
        return None
    
    def get_is_completed(self, obj):
        return obj.status == 'completed'


class TestResultSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='session.test.title', read_only=True)
    user_name = serializers.CharField(source='session.user.full_name', read_only=True)
    generated_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'session', 'test_title', 'user_name', 'total_score', 'max_score',
            'percentage', 'interpretation', 'recommendations', 'generated_at', 'generated_at_persian'
        ]
    
    def get_generated_at_persian(self, obj):
        import jdatetime
        if obj.generated_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.generated_at)
            return jalali_date.strftime('%Y/%m/%d')
        return None


