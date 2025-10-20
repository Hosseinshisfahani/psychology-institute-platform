from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.blog.models import Post, Category, Tag, Comment
from app.courses.models import Course, Enrollment
# from app.therapy_sessions.models import Session, Therapist, SessionBooking, SessionType  # Commented out - therapy_sessions app doesn't exist
from app.dashboard.models import Activity, Notification
from app.workshops.models import (
    Workshop, WorkshopCategory, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview
)
from app.packages.models import Package, PackageCategory, PackagePurchase
import jdatetime

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
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_slug = serializers.CharField(source='post.slug', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    updated_at_persian = serializers.SerializerMethodField()
    is_approved_display = serializers.CharField(source='get_is_approved_display', read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'post_title', 'post_slug', 'author', 'author_name',
            'author_email', 'content', 'is_approved', 'is_approved_display',
            'parent', 'replies_count', 'created_at', 'created_at_persian',
            'updated_at', 'updated_at_persian'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
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
    
    def get_replies_count(self, obj):
        return Comment.objects.filter(parent=obj).count()


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
            'meeting_link', 'meeting_id', 'meeting_password', 'recording_url',
            'materials', 'homework', 'is_completed', 'has_meeting_link',
            'attendance_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_scheduled_datetime_persian(self, obj):
        if obj.scheduled_datetime:
            return jdatetime.datetime.fromgregorian(datetime=obj.scheduled_datetime).strftime('%Y/%m/%d - %H:%M')
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
    
    def get_duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours} ساعت {minutes} دقیقه" if minutes > 0 else f"{hours} ساعت"
        return f"{minutes} دقیقه"
    
    def get_has_meeting_link(self, obj):
        return bool(obj.meeting_link)
    
    def get_attendance_count(self, obj):
        return WorkshopSessionAttendance.objects.filter(session=obj, attended=True).count()


class AdminWorkshopRegistrationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    workshop_title = serializers.CharField(source='workshop.title', read_only=True)
    registered_at_persian = serializers.SerializerMethodField()
    completed_at_persian = serializers.SerializerMethodField()
    last_accessed_persian = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkshopRegistration
        fields = [
            'id', 'user', 'user_name', 'user_email', 'workshop', 'workshop_title',
            'status', 'payment_type', 'amount_paid', 'total_amount',
            'progress_percentage', 'registered_at', 'registered_at_persian',
            'completed_at', 'completed_at_persian', 'last_accessed',
            'last_accessed_persian', 'payment_status'
        ]
        read_only_fields = ['id', 'registered_at', 'completed_at', 'last_accessed']
    
    def get_registered_at_persian(self, obj):
        if obj.registered_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.registered_at).strftime('%Y/%m/%d %H:%M')
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
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'payment_type', 'installment_months', 'installment_amount',
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
            jdate = jdatetime.date.fromgregorian(date=obj.start_date)
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
