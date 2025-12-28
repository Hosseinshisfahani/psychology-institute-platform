from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.blog.models import Post, Category, Tag, Comment
from app.courses.models import Course, Enrollment, CourseComment
# from app.therapy_sessions.models import Session, Therapist, SessionBooking, SessionType  # Commented out - therapy_sessions app doesn't exist
from app.dashboard.models import Activity, Notification
from app.workshops.models import (
    Workshop, WorkshopCategory, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview
)
from app.packages.models import Package, PackageCategory, PackagePurchase, PackageComment
import jdatetime
from datetime import datetime
from django.utils import timezone

User = get_user_model()

class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    user_type_display = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    last_login_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone_number',
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
    
    def get_user_type_display(self, obj):
        return obj.get_user_type_display()


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_last_login_persian(self, obj):
        if obj.last_login:
            return jdatetime.datetime.fromgregorian(datetime=obj.last_login).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance

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


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_view_count(self, obj):
        # This would need to be implemented based on your view tracking system
        return 0

class AdminCourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'instructor', 'instructor_name', 'category',
            'price', 'discount_price', 'status', 'enrollment_count', 'revenue',
            'thumbnail', 'created_at', 'created_at_persian'
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
    
    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        request = self.context.get('request')
        url = obj.thumbnail.url
        if request:
            return request.build_absolute_uri(url)
        return url
    
    def get_category(self, obj):
        if not obj.category:
            return None
        return {
            'id': obj.category.id,
            'name': obj.category.name,
        }


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance

# AdminSessionSerializer commented out - therapy_sessions app doesn't exist
# class AdminSessionSerializer(serializers.ModelSerializer):
#     user_name = serializers.CharField(source='user.get_full_name', read_only=True)
#     therapist_name = serializers.CharField(source='therapist.get_full_name', read_only=True)
#     start_time_persian = serializers.SerializerMethodField()
#     
#     class Meta:
#         model = Session
#         fields = [
#             'id', 'user', 'user_name', 'therapist', 'therapist_name',
#             'session_type', 'start_time', 'end_time', 'start_time_persian',
#             'status', 'rating', 'feedback', 'created_at'
#         ]
#     
#     def get_start_time_persian(self, obj):
#         if obj.start_time:
#             return jdatetime.datetime.fromgregorian(datetime=obj.start_time).strftime('%Y/%m/%d %H:%M')
#         return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance

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


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance

class AdminNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    type = serializers.CharField(source='notification_type', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'title', 'message', 'type',
            'is_read', 'created_at', 'created_at_persian'
        ]
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance

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


# AdminAppointmentSerializer commented out due to therapy_sessions app deletion
# class AdminAppointmentSerializer(serializers.ModelSerializer):
#     client_name = serializers.CharField(source='user.get_full_name', read_only=True)
#     client_email = serializers.CharField(source='user.email', read_only=True)
#     therapist_name = serializers.CharField(source='therapist.user.get_full_name', read_only=True)
#     therapist_specialization = serializers.CharField(source='therapist.specialization', read_only=True)
#     session_type_name = serializers.CharField(source='session_type.name', read_only=True)
#     created_at_persian = serializers.SerializerMethodField()
#     preferred_date_persian = serializers.SerializerMethodField()
#     confirmed_date_persian = serializers.SerializerMethodField()
#     
#     class Meta:
#         model = SessionBooking
#         fields = [
#             'id', 'user', 'client_name', 'client_email', 'therapist', 'therapist_name',
#             'therapist_specialization', 'session_type', 'session_type_name', 'status',
#             'mode', 'preferred_date', 'preferred_time', 'preferred_date_persian',
#             'confirmed_date', 'confirmed_time', 'confirmed_date_persian',
#             'goals', 'notes', 'location', 'price', 'created_at', 'created_at_persian',
#             'expires_at', 'is_expired', 'croom_class_url', 'croom_meeting_id',
#             'croom_password', 'confirmation_notes'
#         ]
#         read_only_fields = ['id', 'created_at', 'expires_at', 'is_expired']
#     
#     def get_created_at_persian(self, obj):
#         if obj.created_at:
#             return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
#         return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_preferred_date_persian(self, obj):
        if obj.preferred_date:
            return jdatetime.datetime.fromgregorian(datetime=obj.preferred_date).strftime('%Y/%m/%d')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_confirmed_date_persian(self, obj):
        if obj.confirmed_date:
            return jdatetime.datetime.fromgregorian(datetime=obj.confirmed_date).strftime('%Y/%m/%d')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance


# AdminTherapistSerializer commented out - therapy_sessions app doesn't exist
# class AdminTherapistSerializer(serializers.ModelSerializer):
#     user_name = serializers.CharField(source='user.get_full_name', read_only=True)
#     user_email = serializers.CharField(source='user.email', read_only=True)
#     user_phone = serializers.CharField(source='user.phone_number', read_only=True)
#     specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
#     created_at_persian = serializers.SerializerMethodField()
#     experience_years = serializers.SerializerMethodField()
#     
#     class Meta:
#         model = Therapist
#         fields = [
#             'id', 'user', 'user_name', 'user_email', 'user_phone', 'specialization',
#             'specialization_display', 'bio', 'education', 'certifications',
#             'experience_start_date', 'experience_years', 'hourly_rate', 'is_available',
#             'profile_image', 'created_at', 'created_at_persian'
#         ]
#         read_only_fields = ['id', 'created_at']
#     
#     def get_created_at_persian(self, obj):
#         if obj.created_at:
#             return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
#         return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_experience_years(self, obj):
        if obj.experience_start_date:
            from datetime import date
            today = date.today()
            return today.year - obj.experience_start_date.year
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance





# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours} ساعت {minutes} دقیقه" if minutes > 0 else f"{hours} ساعت"
        return f"{minutes} دقیقه"


# Blog Admin Serializers

class AdminBlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    tags_data = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    post_count = serializers.SerializerMethodField()
    
    # Override featured_image to accept both file uploads and URL strings
    featured_image = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'author', 'author_name', 'author_email', 'category', 'category_name', 
            'category_color', 'tags', 'tags_data', 'status', 'status_display',
            'is_featured', 'allow_comments', 'view_count', 'like_count',
            'created_at', 'created_at_persian', 'updated_at', 'updated_at_persian',
            'published_at', 'published_at_persian', 'post_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count', 'like_count']
    
    def create(self, validated_data):
        """
        Handle featured_image if it's a URL string (already uploaded)
        """
        # ManyToMany fields must be removed before Post.objects.create(...)
        tags = validated_data.pop('tags', [])
        featured_image = validated_data.pop('featured_image', None)
        image_path = None
        
        # If featured_image is a URL string, extract the path
        if isinstance(featured_image, str) and featured_image.strip():
            # Remove /media/ prefix if present
            if featured_image.startswith('/media/'):
                image_path = featured_image.replace('/media/', '')
            # If it's a full URL, extract the path
            elif featured_image.startswith('http'):
                from urllib.parse import urlparse
                try:
                    parsed = urlparse(featured_image)
                    path = parsed.path
                    if path.startswith('/media/'):
                        image_path = path.replace('/media/', '')
                except Exception:
                    image_path = None
            else:
                # Assume it's already a relative path
                image_path = featured_image
        
        # Create the post first (log full traceback if something fails)
        try:
            post = Post.objects.create(**validated_data)
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"AdminBlogPostSerializer.create failed: {e}")
            logger.error(traceback.format_exc())
            raise

        # Set M2M tags after instance exists
        try:
            if tags is not None:
                post.tags.set(tags)
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"AdminBlogPostSerializer.create tags.set failed: {e}")
            logger.error(traceback.format_exc())
            raise
        
        # If we have a path string, set it on the model
        if image_path:
            try:
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                import logging
                logger = logging.getLogger(__name__)
                
                # Check if file exists in storage
                if default_storage.exists(image_path):
                    # Read the file content
                    with default_storage.open(image_path, 'rb') as f:
                        file_content = f.read()
                    
                    # Get the filename from the path
                    filename = image_path.split('/')[-1]
                    
                    # Create a ContentFile from the content and save to ImageField
                    post.featured_image.save(
                        filename,
                        ContentFile(file_content),
                        save=True
                    )
                    logger.info(f"Successfully set featured_image from path: {image_path}")
                else:
                    logger.warning(f"File does not exist at path: {image_path}")
            except Exception as e:
                # Log the error but don't fail the creation
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to set featured_image: {e}")
                logger.error(traceback.format_exc())
        
        return post
    
    def update(self, instance, validated_data):
        """
        Handle featured_image if it's a URL string (already uploaded)
        """
        # ManyToMany fields must be handled separately
        tags = validated_data.pop('tags', None)
        featured_image = validated_data.pop('featured_image', None)
        image_path = None
        
        # If featured_image is a URL string, extract the path
        if isinstance(featured_image, str) and featured_image.strip():
            # Remove /media/ prefix if present
            if featured_image.startswith('/media/'):
                image_path = featured_image.replace('/media/', '')
            # If it's a full URL, extract the path
            elif featured_image.startswith('http'):
                from urllib.parse import urlparse
                try:
                    parsed = urlparse(featured_image)
                    path = parsed.path
                    if path.startswith('/media/'):
                        image_path = path.replace('/media/', '')
                except Exception:
                    image_path = None
            else:
                # Assume it's already a relative path
                image_path = featured_image
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Set M2M tags after saving
        if tags is not None:
            try:
                instance.tags.set(tags)
            except Exception as e:
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f"AdminBlogPostSerializer.update tags.set failed: {e}")
                logger.error(traceback.format_exc())
                raise
        
        # Handle featured_image
        if image_path:
            try:
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                
                # Check if file exists in storage
                if default_storage.exists(image_path):
                    # Read the file content
                    with default_storage.open(image_path, 'rb') as f:
                        file_content = f.read()
                    
                    # Get the filename from the path
                    filename = image_path.split('/')[-1]
                    
                    # Create a ContentFile from the content and save to ImageField
                    instance.featured_image.save(
                        filename,
                        ContentFile(file_content),
                        save=True
                    )
                    logger.info(f"Successfully updated featured_image from path: {image_path}")
                else:
                    logger.warning(f"File does not exist at path: {image_path}")
            except Exception as e:
                # Log the error but don't fail the update
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to update featured_image: {e}")
                logger.error(traceback.format_exc())
        elif featured_image is None or featured_image == '':
            # Clear featured_image if explicitly set to None or empty
            instance.featured_image = None
            instance.save(update_fields=['featured_image'])
        
        return instance
    
    def get_tags_data(self, obj):
        return [{'id': tag.id, 'name': tag.name, 'slug': tag.slug} for tag in obj.tags.all()]
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_post_count(self, obj):
        # This method doesn't make sense for a Post object, but keeping it for compatibility
        return 1


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_post_count(self, obj):
        return Post.objects.filter(category=obj.category).count()


class AdminCategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'icon',
            'is_active', 'post_count', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_post_count(self, obj):
        return Post.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance


class AdminTagSerializer(serializers.ModelSerializer):
    usage_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'slug', 'usage_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_usage_count(self, obj):
        return Post.objects.filter(tags=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance


class AdminCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_slug = serializers.CharField(source='post.slug', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    is_approved_display = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'post_title', 'post_slug', 'author', 'author_name',
            'author_email', 'content', 'is_approved', 'is_approved_display',
            'parent', 'replies_count', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian'
        ]
        read_only_fields = ['id', 'post', 'author', 'content', 'parent', 'created_at', 'updated_at']
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_is_approved_display(self, obj):
        return 'تایید شده' if obj.is_approved else 'در انتظار تایید'
    
    def get_replies_count(self, obj):
        return Comment.objects.filter(parent=obj).count()


class AdminCourseCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    is_approved_display = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseComment
        fields = [
            'id', 'course', 'course_title', 'course_slug', 'author', 'author_name',
            'author_email', 'content', 'is_approved', 'is_approved_display',
            'parent', 'replies_count', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian'
        ]
        read_only_fields = ['id', 'course', 'author', 'content', 'parent', 'created_at', 'updated_at']
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_is_approved_display(self, obj):
        return 'تایید شده' if obj.is_approved else 'در انتظار تایید'
    
    def get_replies_count(self, obj):
        return CourseComment.objects.filter(parent=obj).count()


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
# Workshop Admin Serializers

class AdminWorkshopCategorySerializer(serializers.ModelSerializer):
    workshop_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkshopCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'workshop_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_workshop_count(self, obj):
        return Workshop.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance


class AdminWorkshopSessionSerializer(serializers.ModelSerializer):
    scheduled_datetime_persian = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    has_meeting_link = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkshopSession
        fields = [
            'id', 'session_number', 'title', 'description', 'scheduled_datetime',
            'scheduled_datetime_persian', 'duration_minutes', 'duration_display',
            'session_video', 'croom_platform_link',
            'materials', 'homework', 'is_completed', 'has_meeting_link',
            'attendance_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_scheduled_datetime_persian(self, obj):
        if obj.scheduled_datetime:
            # Check if the datetime is already in Persian format (year between 1300-1500)
            if hasattr(obj.scheduled_datetime, 'year') and 1300 <= obj.scheduled_datetime.year <= 1500:
                # Datetime is already in Persian calendar, just format it
                return obj.scheduled_datetime.strftime('%Y/%m/%d - %H:%M')
            else:
                # Datetime is in Gregorian calendar, convert to Persian
                try:
                    jdatetime_obj = jdatetime.datetime.fromgregorian(datetime=obj.scheduled_datetime)
                    return jdatetime_obj.strftime('%Y/%m/%d - %H:%M')
                except Exception:
                    return obj.scheduled_datetime.strftime('%Y/%m/%d - %H:%M')
        return None
    
    def get_duration_display(self, obj):
        """Return duration in a human-readable format"""
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0 and minutes > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        elif hours > 0:
            return f"{hours} ساعت"
        else:
            return f"{minutes} دقیقه"
    
    def get_has_meeting_link(self, obj):
        """Check if session has a meeting link"""
        return bool(obj.croom_platform_link)
    
    def get_attendance_count(self, obj):
        """Get count of attendees who attended"""
        from app.workshops.models import WorkshopSessionAttendance
        return WorkshopSessionAttendance.objects.filter(session=obj, attended=True).count()


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours} ساعت {minutes} دقیقه" if minutes > 0 else f"{hours} ساعت"
        return f"{minutes} دقیقه"
    


class InstallmentPaymentAdminSerializer(serializers.ModelSerializer):
    due_date_persian = serializers.SerializerMethodField()
    paid_at_persian = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = InstallmentPayment
        fields = [
            'id', 'installment_number', 'amount', 'due_date', 'due_date_persian',
            'status', 'paid_at', 'paid_at_persian', 'is_overdue'
        ]
    
    def get_due_date_persian(self, obj):
        if obj.due_date:
            jdate = jdatetime.date.fromgregorian(date=obj.due_date)
            return jdate.strftime('%Y/%m/%d')
        return None
    
    def get_paid_at_persian(self, obj):
        if obj.paid_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.paid_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_is_overdue(self, obj):
        if obj.status == 'pending' and obj.due_date:
            return obj.due_date < timezone.now().date()
        return False


class InstallmentPlanAdminSerializer(serializers.ModelSerializer):
    payments = InstallmentPaymentAdminSerializer(many=True, read_only=True)
    total_paid = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    is_fully_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = InstallmentPlan
        fields = [
            'id', 'total_amount', 'number_of_installments', 'installment_amount',
            'total_paid', 'remaining_amount', 'is_fully_paid', 'payments'
        ]
    
    def get_total_paid(self, obj):
        return sum(float(payment.amount) for payment in obj.payments.filter(status='paid'))
    
    def get_remaining_amount(self, obj):
        return float(obj.total_amount) - self.get_total_paid(obj)
    
    def get_is_fully_paid(self, obj):
        return obj.payments.filter(status='paid').count() == obj.number_of_installments


class AdminWorkshopRegistrationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    workshop_title = serializers.CharField(source='workshop.title', read_only=True)
    registered_at_persian = serializers.SerializerMethodField()
    completed_at_persian = serializers.SerializerMethodField()
    last_accessed_persian = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    installment_plan = InstallmentPlanAdminSerializer(read_only=True)
    
    class Meta:
        model = WorkshopRegistration
        fields = [
            'id', 'user', 'user_name', 'user_email', 'workshop', 'workshop_title',
            'status', 'payment_type', 'amount_paid', 'total_amount',
            'progress_percentage', 'registered_at', 'registered_at_persian',
            'completed_at', 'completed_at_persian', 'last_accessed',
            'last_accessed_persian', 'payment_status', 'installment_plan'
        ]
        read_only_fields = ['id', 'registered_at', 'completed_at', 'last_accessed']
    
    def get_registered_at_persian(self, obj):
        if obj.registered_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.registered_at).strftime('%Y/%m/%d %H:%M')
        return None

    def get_completed_at_persian(self, obj):
        if obj.completed_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.completed_at).strftime('%Y/%m/%d %H:%M')
        return None

    def get_last_accessed_persian(self, obj):
        if obj.last_accessed:
            return jdatetime.datetime.fromgregorian(datetime=obj.last_accessed).strftime('%Y/%m/%d %H:%M')
        return None

    def get_payment_status(self, obj):
        if obj.payment_type == 'full_payment':
            return 'پرداخت کامل' if obj.amount_paid >= obj.total_amount else 'در انتظار پرداخت'
        else:
            return 'قسطی' if obj.amount_paid > 0 else 'در انتظار پرداخت'


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_completed_at_persian(self, obj):
        if obj.completed_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.completed_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_last_accessed_persian(self, obj):
        if obj.last_accessed:
            return jdatetime.datetime.fromgregorian(datetime=obj.last_accessed).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_payment_status(self, obj):
        if obj.payment_type == 'full_payment':
            return 'پرداخت کامل' if obj.amount_paid >= obj.total_amount else 'در انتظار پرداخت'
        else:
            return 'قسطی' if obj.amount_paid > 0 else 'در انتظار پرداخت'


class AdminWorkshopSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    instructor_email = serializers.CharField(source='instructor.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    sessions = AdminWorkshopSessionSerializer(many=True, read_only=True)
    registrations = AdminWorkshopRegistrationSerializer(many=True, read_only=True)
    
    # Statistics
    registration_count = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    
    # Persian dates
    start_date_persian = serializers.SerializerMethodField()
    end_date_persian = serializers.SerializerMethodField()
    registration_deadline_persian = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    # Persian prices
    price_persian = serializers.SerializerMethodField()
    discount_price_persian = serializers.SerializerMethodField()
    current_price_persian = serializers.SerializerMethodField()
    installment_amount_persian = serializers.SerializerMethodField()
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    installment_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Workshop
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'instructor',
            'instructor_name', 'instructor_email', 'status', 'difficulty',
            'price', 'price_persian', 'discount_price', 'discount_price_persian', 
            'current_price', 'current_price_persian', 'discount_percentage',
            'payment_type', 'installment_months', 'installment_amount', 'installment_amount_persian',
            'start_date', 'start_date_persian', 'end_date', 'end_date_persian',
            'registration_deadline', 'registration_deadline_persian',
            'total_hours', 'language', 'prerequisites', 'learning_objectives',
            'current_participants', 'max_participants', 'is_full', 'available_seats',
            'thumbnail', 'intro_video', 'rating', 'review_count',
            'registration_count', 'attendance_rate', 'revenue',
            'created_at', 'created_at_persian', 'published_at', 'published_at_persian',
            'sessions', 'registrations'
        ]
        read_only_fields = ['id', 'created_at', 'published_at', 'rating', 'review_count']
    
    def get_registration_count(self, obj):
        return WorkshopRegistration.objects.filter(workshop=obj).count()
    
    def get_attendance_rate(self, obj):
        total_sessions = obj.sessions.count()
        if total_sessions == 0:
            return 0
        total_attendance = WorkshopSessionAttendance.objects.filter(
            session__workshop=obj, attended=True
        ).count()
        return round((total_attendance / (total_sessions * obj.current_participants)) * 100, 1) if obj.current_participants > 0 else 0
    
    def get_revenue(self, obj):
        registrations = WorkshopRegistration.objects.filter(workshop=obj)
        return sum(float(reg.amount_paid) for reg in registrations)
    
    def get_start_date_persian(self, obj):
        if obj.start_date:
            # Check if the date is already in Persian format (year between 1300-1500)
            if hasattr(obj.start_date, 'year') and 1300 <= obj.start_date.year <= 1500:
                # Date is already in Persian calendar, just format it
                return obj.start_date.strftime('%Y/%m/%d')
            else:
                # Date is in Gregorian calendar, convert to Persian
                try:
                    jdate = jdatetime.date.fromgregorian(date=obj.start_date)
                    return jdate.strftime('%Y/%m/%d')
                except Exception:
                    return obj.start_date.strftime('%Y/%m/%d')
        return None
    
    def get_end_date_persian(self, obj):
        if obj.end_date:
            # Check if the date is already in Persian format (year between 1300-1500)
            if hasattr(obj.end_date, 'year') and 1300 <= obj.end_date.year <= 1500:
                # Date is already in Persian calendar, just format it
                return obj.end_date.strftime('%Y/%m/%d')
            else:
                # Date is in Gregorian calendar, convert to Persian
                try:
                    jdate = jdatetime.date.fromgregorian(date=obj.end_date)
                    return jdate.strftime('%Y/%m/%d')
                except Exception:
                    return obj.end_date.strftime('%Y/%m/%d')
        return None
    
    def get_registration_deadline_persian(self, obj):
        if obj.registration_deadline:
            # Check if the datetime is already in Persian format (year between 1300-1500)
            if hasattr(obj.registration_deadline, 'year') and 1300 <= obj.registration_deadline.year <= 1500:
                # Datetime is already in Persian calendar, just format it
                return obj.registration_deadline.strftime('%Y/%m/%d %H:%M')
            else:
                # Datetime is in Gregorian calendar, convert to Persian
                try:
                    jdatetime_obj = jdatetime.datetime.fromgregorian(datetime=obj.registration_deadline)
                    return jdatetime_obj.strftime('%Y/%m/%d %H:%M')
                except Exception:
                    return obj.registration_deadline.strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            try:
                jdatetime_obj = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
                return jdatetime_obj.strftime('%Y/%m/%d %H:%M')
            except Exception:
                return obj.created_at.strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            try:
                jdatetime_obj = jdatetime.datetime.fromgregorian(datetime=obj.published_at)
                return jdatetime_obj.strftime('%Y/%m/%d %H:%M')
            except Exception:
                return obj.published_at.strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_price_persian(self, obj):
        if obj.price:
            return f"{obj.price:,.0f} تومان"
        return None
    
    def get_discount_price_persian(self, obj):
        if obj.discount_price:
            return f"{obj.discount_price:,.0f} تومان"
        return None
    
    def get_current_price_persian(self, obj):
        if obj.current_price:
            return f"{obj.current_price:,.0f} تومان"
        return None
    
    def get_installment_amount_persian(self, obj):
        if obj.installment_amount:
            return f"{obj.installment_amount:,.0f} تومان"
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_end_date_persian(self, obj):
        if obj.end_date:
            jdate = jdatetime.date.fromgregorian(date=obj.end_date)
            return jdate.strftime('%Y/%m/%d')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_registration_deadline_persian(self, obj):
        if obj.registration_deadline:
            return jdatetime.datetime.fromgregorian(datetime=obj.registration_deadline).strftime('%Y/%m/%d - %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None


# Package Admin Serializers

class AdminPackageCategorySerializer(serializers.ModelSerializer):
    package_count = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_active', 'package_count', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_package_count(self, obj):
        return Package.objects.filter(category=obj).count()
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package admin"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail', 'status'
        ]


class AdminPackageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    # Statistics
    revenue = serializers.SerializerMethodField()
    purchase_count = serializers.IntegerField(read_only=True)
    
    # Persian dates
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'category_name', 'category_color', 'status',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'is_featured', 'duration_months', 'language', 'prerequisites',
            'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'course_ids', 'total_courses', 'total_hours',
            'original_total_price', 'savings_amount', 'savings_percentage',
            'purchase_count', 'revenue', 'rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian', 'published_at', 'published_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at', 'rating', 'review_count']
    
    def get_revenue(self, obj):
        purchases = PackagePurchase.objects.filter(package=obj)
        return sum(float(purchase.amount_paid) for purchase in purchases)
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = Package.objects.create(**validated_data)
        
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        
        return package
    
    def update(self, instance, validated_data):
        course_ids = validated_data.pop('course_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if course_ids is not None:
            courses = Course.objects.filter(id__in=course_ids)
            instance.courses.set(courses)
        
        return instance


class AdminWorkshopReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='registration.user.full_name', read_only=True)
    author_email = serializers.CharField(source='registration.user.email', read_only=True)
    workshop_title = serializers.CharField(source='registration.workshop.title', read_only=True)
    workshop_slug = serializers.CharField(source='registration.workshop.slug', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    is_approved_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkshopReview
        fields = [
            'id', 'registration', 'workshop_title', 'workshop_slug', 'author_name',
            'author_email', 'rating', 'title', 'content', 'instructor_rating',
            'content_rating', 'interaction_rating', 'is_approved', 'is_approved_display',
            'created_at', 'created_at_persian', 'updated_at', 'updated_at_persian'
        ]
        read_only_fields = ['id', 'registration', 'created_at', 'updated_at']
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_is_approved_display(self, obj):
        return 'تایید شده' if obj.is_approved else 'در انتظار تایید'


class AdminPackageCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    package_title = serializers.CharField(source='package.title', read_only=True)
    package_slug = serializers.CharField(source='package.slug', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    is_approved_display = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageComment
        fields = [
            'id', 'package', 'package_title', 'package_slug', 'author', 'author_name',
            'author_email', 'content', 'is_approved', 'is_approved_display',
            'parent', 'replies_count', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian'
        ]
        read_only_fields = ['id', 'package', 'author', 'content', 'parent', 'created_at', 'updated_at']
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_updated_at_persian(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_is_approved_display(self, obj):
        return 'تایید شده' if obj.is_approved else 'در انتظار تایید'
    
    def get_replies_count(self, obj):
        return PackageComment.objects.filter(parent=obj).count()
