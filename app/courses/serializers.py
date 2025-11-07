from rest_framework import serializers
from .models import Course, Lesson, Enrollment, LessonProgress, CourseCategory, CourseVideo
from django.contrib.auth import get_user_model
from django.utils import timezone
import jdatetime

User = get_user_model()

class CourseVideoSerializer(serializers.ModelSerializer):
    """Serializer for CourseVideo model"""
    attachment_file_name = serializers.SerializerMethodField()
    attachment_file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseVideo
        fields = [
            'id', 'title', 'description', 'video_file', 'video_url', 
            'attachment_file', 'attachment_file_name', 'attachment_file_size',
            'duration_minutes', 'order', 'is_preview', 'allow_download', 
            'is_active', 'created_at'
        ]
    
    def get_attachment_file_name(self, obj):
        if obj.attachment_file:
            return obj.attachment_file.name.split('/')[-1]
        return None
    
    def get_attachment_file_size(self, obj):
        if obj.attachment_file:
            try:
                size = obj.attachment_file.size
                # Convert to human readable format
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
            except:
                return None
        return None

class LessonSerializer(serializers.ModelSerializer):
    duration_formatted = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'video_url', 'video_file',
            'duration_formatted', 'order', 'is_preview', 'is_completed'
        ]
    
    def get_duration_formatted(self, obj):
        if obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:00"
            else:
                return f"{minutes}:00"
        return "00:00"
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                # Get enrollment for the course (via module)
                enrollment = Enrollment.objects.get(
                    user=request.user,
                    course=obj.module.course
                )
                # Check lesson progress
                progress = LessonProgress.objects.get(
                    enrollment=enrollment,
                    lesson=obj
                )
                return progress.is_completed
            except (Enrollment.DoesNotExist, LessonProgress.DoesNotExist):
                return False
        return False

class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
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
            'id', 'title', 'slug', 'description',
            'thumbnail', 'price', 'discount_price', 'level',
            'category', 'instructor_name', 'created_at', 'created_at_persian',
            'lessons', 'enrollment_status', 'progress_percentage',
            'completed_lessons', 'total_lessons', 'total_duration'
        ]
    
    def get_lessons(self, obj):
        # Get all lessons from all modules, ordered by module order and lesson order
        lessons = Lesson.objects.filter(module__course=obj).order_by('module__order', 'order')
        return LessonSerializer(lessons, many=True, context=self.context).data
    
    def get_enrollment_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(user=request.user, course=obj)
                return {
                    'is_enrolled': True,
                    'enrollment_date': enrollment.enrolled_at,
                    'is_completed': enrollment.status == 'completed',
                }
            except Enrollment.DoesNotExist:
                return {'is_enrolled': False}
        return {'is_enrolled': False}
    
    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            total_lessons = Lesson.objects.filter(module__course=obj).count()
            if total_lessons == 0:
                return 0
            
            try:
                enrollment = Enrollment.objects.get(user=request.user, course=obj)
                completed_lessons = LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson__module__course=obj,
                    is_completed=True
                ).count()
                
                return round((completed_lessons / total_lessons) * 100, 1)
            except Enrollment.DoesNotExist:
                return 0
        return 0
    
    def get_completed_lessons(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(user=request.user, course=obj)
                return LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson__module__course=obj,
                    is_completed=True
                ).count()
            except Enrollment.DoesNotExist:
                return 0
        return 0
    
    def get_total_lessons(self, obj):
        return Lesson.objects.filter(module__course=obj).count()
    
    def get_total_duration(self, obj):
        lessons = Lesson.objects.filter(module__course=obj)
        total_minutes = sum(
            lesson.duration_minutes if lesson.duration_minutes else 0 
            for lesson in lessons
        )
        
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        
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


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color']


class CourseDetailPublicSerializer(serializers.ModelSerializer):
    """Public serializer for course detail page (no authentication required)"""
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    created_at_persian = serializers.SerializerMethodField()
    enrollment_count = serializers.ReadOnlyField()
    rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    videos = serializers.SerializerMethodField()
    enrollment_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description', 'thumbnail', 'video_intro',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_free', 'difficulty', 'duration_hours', 'language', 'level',
            'instructor_name', 'category_name', 'category_slug',
            'enrollment_count', 'rating', 'review_count',
            'prerequisites', 'learning_objectives',
            'created_at', 'created_at_persian', 'published_at',
            'videos', 'enrollment_status'
        ]
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d')
        return None
    
    def get_videos(self, obj):
        # Only return active videos
        videos = obj.videos.filter(is_active=True).order_by('order', 'created_at')
        return CourseVideoSerializer(videos, many=True, context=self.context).data
    
    def get_enrollment_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(user=request.user, course=obj)
                return {
                    'is_enrolled': True,
                    'enrolled_at': enrollment.enrolled_at,
                    'status': enrollment.status,
                }
            except Enrollment.DoesNotExist:
                # Check if purchased
                from .models import CoursePurchase
                if CoursePurchase.objects.filter(user=request.user, course=obj).exists():
                    return {
                        'is_enrolled': True,
                        'is_purchased': True,
                    }
                return {'is_enrolled': False}
        return {'is_enrolled': False}


class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    created_at_persian = serializers.SerializerMethodField()
    enrollment_count = serializers.ReadOnlyField()
    rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'thumbnail',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_free', 'difficulty', 'duration_hours', 'language', 'level',
            'instructor_name', 'category_name', 'category_slug',
            'enrollment_count', 'rating', 'review_count',
            'created_at', 'created_at_persian'
        ]
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d')
        return None
