from rest_framework import serializers
from .models import Course, Lesson, Enrollment, LessonProgress
from django.contrib.auth import get_user_model
import jdatetime

User = get_user_model()

class LessonSerializer(serializers.ModelSerializer):
    duration_formatted = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'video_url', 'duration', 
            'duration_formatted', 'order', 'is_free', 'is_completed'
        ]
    
    def get_duration_formatted(self, obj):
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        return "00:00"
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = LessonProgress.objects.get(
                    user=request.user,
                    lesson=obj
                )
                return progress.is_completed
            except LessonProgress.DoesNotExist:
                return False
        return False

class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    enrollment_status = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'long_description',
            'featured_image', 'price', 'discount_price', 'level',
            'category', 'instructor_name', 'created_at', 'created_at_persian',
            'lessons', 'enrollment_status', 'progress_percentage',
            'completed_lessons', 'total_lessons', 'total_duration'
        ]
    
    def get_enrollment_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(user=request.user, course=obj)
                return {
                    'is_enrolled': True,
                    'enrollment_date': enrollment.enrollment_date,
                    'is_completed': enrollment.is_completed,
                }
            except Enrollment.DoesNotExist:
                return {'is_enrolled': False}
        return {'is_enrolled': False}
    
    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            total_lessons = obj.lessons.count()
            if total_lessons == 0:
                return 0
            
            completed_lessons = LessonProgress.objects.filter(
                user=request.user,
                lesson__course=obj,
                is_completed=True
            ).count()
            
            return round((completed_lessons / total_lessons) * 100, 1)
        return 0
    
    def get_completed_lessons(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LessonProgress.objects.filter(
                user=request.user,
                lesson__course=obj,
                is_completed=True
            ).count()
        return 0
    
    def get_total_lessons(self, obj):
        return obj.lessons.count()
    
    def get_total_duration(self, obj):
        total_seconds = sum(
            lesson.duration.total_seconds() if lesson.duration else 0 
            for lesson in obj.lessons.all()
        )
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        else:
            return f"{minutes} دقیقه"
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d')
        return None

class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = ['id', 'lesson', 'lesson_title', 'is_completed', 'completed_at', 'watch_time']
        read_only_fields = ['completed_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'course_slug', 'enrollment_date', 'is_completed']
        read_only_fields = ['enrollment_date']
