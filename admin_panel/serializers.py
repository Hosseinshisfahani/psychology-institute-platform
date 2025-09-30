from rest_framework import serializers
from django.contrib.auth import get_user_model
from blog.models import Post, Category
from courses.models import Course, Enrollment
from therapy_sessions.models import Session, Therapist
from dashboard.models import Activity, Notification
import jdatetime

User = get_user_model()

class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    last_login_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'user_type', 'user_type_display', 'is_active', 'is_staff',
            'date_joined', 'created_at_persian', 'last_login', 'last_login_persian'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_created_at_persian(self, obj):
        if obj.date_joined:
            return jdatetime.datetime.fromgregorian(datetime=obj.date_joined).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_last_login_persian(self, obj):
        if obj.last_login:
            return jdatetime.datetime.fromgregorian(datetime=obj.last_login).strftime('%Y/%m/%d %H:%M')
        return None

class AdminPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    view_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 'author_name',
            'category', 'category_name', 'status', 'featured_image',
            'created_at', 'created_at_persian', 'updated_at', 'view_count'
        ]
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_view_count(self, obj):
        # This would need to be implemented based on your view tracking system
        return 0

class AdminCourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'instructor', 'instructor_name',
            'price', 'discount_price', 'status', 'enrollment_count', 'revenue',
            'created_at', 'created_at_persian'
        ]
    
    def get_enrollment_count(self, obj):
        return Enrollment.objects.filter(course=obj).count()
    
    def get_revenue(self, obj):
        enrollments = Enrollment.objects.filter(course=obj)
        total_revenue = sum(enrollment.course.price for enrollment in enrollments)
        return total_revenue
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None

class AdminSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    therapist_name = serializers.CharField(source='therapist.get_full_name', read_only=True)
    start_time_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = [
            'id', 'user', 'user_name', 'therapist', 'therapist_name',
            'session_type', 'start_time', 'end_time', 'start_time_persian',
            'status', 'rating', 'feedback', 'created_at'
        ]
    
    def get_start_time_persian(self, obj):
        if obj.start_time:
            return jdatetime.datetime.fromgregorian(datetime=obj.start_time).strftime('%Y/%m/%d %H:%M')
        return None

class AdminActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = [
            'id', 'user', 'user_name', 'activity_type', 'description',
            'metadata', 'created_at', 'created_at_persian'
        ]
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None

class AdminNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'title', 'message', 'type',
            'is_read', 'action_url', 'created_at', 'created_at_persian'
        ]
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None

class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=0)
    active_users = serializers.IntegerField()
    pending_sessions = serializers.IntegerField()
    new_users_this_month = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    average_session_rating = serializers.FloatField()
    monthly_revenue = serializers.DecimalField(max_digits=10, decimal_places=0)
