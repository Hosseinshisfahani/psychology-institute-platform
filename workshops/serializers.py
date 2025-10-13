from rest_framework import serializers
from .models import (
    Workshop, WorkshopCategory, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview
)
from django.contrib.auth import get_user_model
import jdatetime

User = get_user_model()


class WorkshopCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkshopCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color']


class WorkshopSessionSerializer(serializers.ModelSerializer):
    scheduled_datetime_persian = serializers.SerializerMethodField()
    has_recording = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkshopSession
        fields = [
            'id', 'session_number', 'title', 'description',
            'scheduled_datetime', 'scheduled_datetime_persian',
            'duration_minutes', 'meeting_link', 'recording_url',
            'has_recording', 'can_join', 'is_completed'
        ]
    
    def get_scheduled_datetime_persian(self, obj):
        if obj.scheduled_datetime:
            return jdatetime.datetime.fromgregorian(datetime=obj.scheduled_datetime).strftime('%Y/%m/%d - %H:%M')
        return None
    
    def get_has_recording(self, obj):
        return bool(obj.recording_url)
    
    def get_can_join(self, obj):
        """Check if session is currently joinable"""
        from django.utils import timezone
        now = timezone.now()
        # Can join 15 minutes before and anytime after
        return (obj.scheduled_datetime - timezone.timedelta(minutes=15)) <= now


class WorkshopListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    start_date_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Workshop
        fields = [
            'id', 'title', 'slug', 'short_description', 'category_name',
            'instructor_name', 'status', 'difficulty', 'price', 'discount_price',
            'current_price', 'discount_percentage', 'start_date', 'start_date_persian',
            'end_date', 'total_hours', 'current_participants', 'max_participants',
            'is_full', 'available_seats', 'thumbnail', 'rating', 'payment_type'
        ]
    
    def get_start_date_persian(self, obj):
        if obj.start_date:
            jdate = jdatetime.date.fromgregorian(date=obj.start_date)
            return jdate.strftime('%Y/%m/%d')
        return None


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    due_date_persian = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InstallmentPayment
        fields = [
            'id', 'installment_number', 'amount', 'due_date', 'due_date_persian',
            'status', 'paid_at', 'is_overdue'
        ]
    
    def get_due_date_persian(self, obj):
        if obj.due_date:
            jdate = jdatetime.date.fromgregorian(date=obj.due_date)
            return jdate.strftime('%Y/%m/%d')
        return None


class InstallmentPlanSerializer(serializers.ModelSerializer):
    payments = InstallmentPaymentSerializer(many=True, read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_fully_paid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InstallmentPlan
        fields = [
            'id', 'total_amount', 'number_of_installments', 'installment_amount',
            'total_paid', 'remaining_amount', 'is_fully_paid', 'payments'
        ]


class WorkshopDetailSerializer(serializers.ModelSerializer):
    category = WorkshopCategorySerializer(read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    sessions = WorkshopSessionSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    installment_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    registration_status = serializers.SerializerMethodField()
    start_date_persian = serializers.SerializerMethodField()
    end_date_persian = serializers.SerializerMethodField()
    registration_deadline_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Workshop
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'instructor_name', 'status', 'difficulty',
            'price', 'discount_price', 'current_price', 'discount_percentage',
            'payment_type', 'installment_months', 'installment_amount',
            'start_date', 'start_date_persian', 'end_date', 'end_date_persian',
            'registration_deadline', 'registration_deadline_persian',
            'total_hours', 'language', 'prerequisites', 'learning_objectives',
            'current_participants', 'max_participants', 'is_full', 'available_seats',
            'thumbnail', 'intro_video', 'rating', 'review_count',
            'sessions', 'registration_status'
        ]
    
    def get_registration_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                registration = WorkshopRegistration.objects.get(user=request.user, workshop=obj)
                return {
                    'is_registered': True,
                    'status': registration.status,
                    'payment_type': registration.payment_type,
                    'progress_percentage': registration.progress_percentage,
                }
            except WorkshopRegistration.DoesNotExist:
                return {'is_registered': False}
        return {'is_registered': False}
    
    def get_start_date_persian(self, obj):
        if obj.start_date:
            jdate = jdatetime.date.fromgregorian(date=obj.start_date)
            return jdate.strftime('%Y/%m/%d')
        return None
    
    def get_end_date_persian(self, obj):
        if obj.end_date:
            jdate = jdatetime.date.fromgregorian(date=obj.end_date)
            return jdate.strftime('%Y/%m/%d')
        return None
    
    def get_registration_deadline_persian(self, obj):
        if obj.registration_deadline:
            return jdatetime.datetime.fromgregorian(datetime=obj.registration_deadline).strftime('%Y/%m/%d - %H:%M')
        return None


class WorkshopRegistrationSerializer(serializers.ModelSerializer):
    workshop = WorkshopListSerializer(read_only=True)
    workshop_id = serializers.IntegerField(write_only=True)
    installment_plan = InstallmentPlanSerializer(read_only=True)
    
    class Meta:
        model = WorkshopRegistration
        fields = [
            'id', 'workshop', 'workshop_id', 'status', 'payment_type',
            'amount_paid', 'total_amount', 'progress_percentage',
            'registered_at', 'installment_plan'
        ]
        read_only_fields = ['status', 'amount_paid', 'progress_percentage', 'registered_at']
    
    def validate_workshop_id(self, value):
        try:
            workshop = Workshop.objects.get(id=value)
            if workshop.is_full:
                raise serializers.ValidationError("این کارگاه ظرفیت کامل دارد")
            if workshop.status != 'registration_open':
                raise serializers.ValidationError("ثبت‌نام برای این کارگاه باز نیست")
        except Workshop.DoesNotExist:
            raise serializers.ValidationError("کارگاه مورد نظر یافت نشد")
        return value
    
    def validate_payment_type(self, value):
        workshop_id = self.initial_data.get('workshop_id')
        if workshop_id:
            try:
                workshop = Workshop.objects.get(id=workshop_id)
                if workshop.payment_type == 'full_payment' and value == 'installment':
                    raise serializers.ValidationError("این کارگاه فقط پرداخت کامل را قبول می‌کند")
                if workshop.payment_type == 'installment' and value == 'full_payment':
                    raise serializers.ValidationError("این کارگاه فقط پرداخت قسطی را قبول می‌کند")
            except Workshop.DoesNotExist:
                pass
        return value


class WorkshopSessionAttendanceSerializer(serializers.ModelSerializer):
    session = WorkshopSessionSerializer(read_only=True)
    
    class Meta:
        model = WorkshopSessionAttendance
        fields = [
            'id', 'session', 'attended', 'join_time', 'leave_time',
            'duration_minutes', 'attendance_marked_at'
        ]
        read_only_fields = ['attendance_marked_at']


class WorkshopReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='registration.user.full_name', read_only=True)
    workshop_title = serializers.CharField(source='registration.workshop.title', read_only=True)
    
    class Meta:
        model = WorkshopReview
        fields = [
            'id', 'rating', 'title', 'content', 'instructor_rating',
            'content_rating', 'interaction_rating', 'user_name',
            'workshop_title', 'created_at'
        ]
        read_only_fields = ['created_at']

