from rest_framework import serializers
from .models import (
    Package, PackageCategory, PackagePurchase, PackageEnrollment,
    PackageProgress, PackageReview, PackageCoupon
)
from courses.models import Course, Enrollment
from courses.serializers import CourseDetailSerializer
from django.contrib.auth import get_user_model
import jdatetime

User = get_user_model()


class PackageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color']


class SimpleCourseSerializer(serializers.ModelSerializer):
    """Simplified course serializer for package listings"""
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'instructor_name',
            'difficulty', 'price', 'discount_price', 'current_price',
            'duration_hours', 'thumbnail'
        ]


class PackageListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'short_description', 'category_name',
            'status', 'price', 'discount_price', 'current_price',
            'discount_percentage', 'is_featured', 'total_courses',
            'total_hours', 'duration_months', 'thumbnail', 'rating',
            'purchase_count', 'savings_amount', 'savings_percentage'
        ]


class PackageDetailSerializer(serializers.ModelSerializer):
    category = PackageCategorySerializer(read_only=True)
    courses = SimpleCourseSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    total_courses = serializers.IntegerField(read_only=True)
    total_hours = serializers.IntegerField(read_only=True)
    original_total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    savings_percentage = serializers.IntegerField(read_only=True)
    purchase_status = serializers.SerializerMethodField()
    published_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'status', 'price', 'discount_price', 'current_price',
            'discount_percentage', 'is_featured', 'duration_months', 'language',
            'prerequisites', 'learning_objectives', 'thumbnail', 'intro_video',
            'courses', 'total_courses', 'total_hours', 'original_total_price',
            'savings_amount', 'savings_percentage', 'purchase_count', 'rating',
            'review_count', 'published_at_persian', 'purchase_status'
        ]
    
    def get_purchase_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                purchase = PackagePurchase.objects.get(user=request.user, package=obj)
                return {
                    'is_purchased': True,
                    'purchased_at': purchase.purchased_at,
                    'is_expired': purchase.is_expired,
                }
            except PackagePurchase.DoesNotExist:
                return {'is_purchased': False}
        return {'is_purchased': False}
    
    def get_published_at_persian(self, obj):
        if obj.published_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.published_at).strftime('%Y/%m/%d')
        return None


class PackageEnrollmentSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer(source='enrollment.course', read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    course_status = serializers.CharField(source='enrollment.status', read_only=True)
    
    class Meta:
        model = PackageEnrollment
        fields = [
            'id', 'course', 'progress_percentage', 'course_status',
            'started_at', 'last_accessed'
        ]


class PackageProgressSerializer(serializers.ModelSerializer):
    package_title = serializers.CharField(source='purchase.package.title', read_only=True)
    total_courses = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageProgress
        fields = [
            'id', 'package_title', 'overall_progress_percentage',
            'completed_courses', 'total_courses', 'total_time_spent', 'updated_at'
        ]
    
    def get_total_courses(self, obj):
        return obj.purchase.package.courses.count()


class PackagePurchaseSerializer(serializers.ModelSerializer):
    package = PackageListSerializer(read_only=True)
    package_id = serializers.IntegerField(write_only=True)
    course_enrollments = PackageEnrollmentSerializer(many=True, read_only=True)
    progress = PackageProgressSerializer(read_only=True)
    
    class Meta:
        model = PackagePurchase
        fields = [
            'id', 'package', 'package_id', 'amount_paid', 'original_price',
            'discount_amount', 'payment_method', 'purchased_at',
            'expires_at', 'course_enrollments', 'progress'
        ]
        read_only_fields = ['amount_paid', 'original_price', 'discount_amount', 'purchased_at']
    
    def validate_package_id(self, value):
        try:
            package = Package.objects.get(id=value)
            if package.status != 'published':
                raise serializers.ValidationError("این بسته در دسترس نیست")
        except Package.DoesNotExist:
            raise serializers.ValidationError("بسته مورد نظر یافت نشد")
        return value
    
    def create(self, validated_data):
        package_id = validated_data.pop('package_id')
        package = Package.objects.get(id=package_id)
        user = self.context['request'].user
        
        # Create purchase
        purchase = PackagePurchase.objects.create(
            user=user,
            package=package,
            amount_paid=package.current_price,
            original_price=package.price,
            discount_amount=package.price - package.current_price if package.discount_price else 0,
            **validated_data
        )
        
        # Create course enrollments
        purchase.create_course_enrollments()
        
        # Create progress tracker
        PackageProgress.objects.create(purchase=purchase)
        
        return purchase


class PackageReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='purchase.user.full_name', read_only=True)
    package_title = serializers.CharField(source='purchase.package.title', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageReview
        fields = [
            'id', 'rating', 'title', 'content', 'value_rating',
            'content_rating', 'support_rating', 'user_name',
            'package_title', 'created_at', 'created_at_persian'
        ]
        read_only_fields = ['created_at']
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d')
        return None


class PackageCouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    valid_from_persian = serializers.SerializerMethodField()
    valid_until_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageCoupon
        fields = [
            'id', 'code', 'title', 'description', 'coupon_type',
            'discount_value', 'min_order_amount', 'max_discount_amount',
            'is_active', 'valid_from', 'valid_from_persian',
            'valid_until', 'valid_until_persian', 'is_valid'
        ]
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
    def get_valid_from_persian(self, obj):
        if obj.valid_from:
            return jdatetime.datetime.fromgregorian(datetime=obj.valid_from).strftime('%Y/%m/%d')
        return None
    
    def get_valid_until_persian(self, obj):
        if obj.valid_until:
            return jdatetime.datetime.fromgregorian(datetime=obj.valid_until).strftime('%Y/%m/%d')
        return None

