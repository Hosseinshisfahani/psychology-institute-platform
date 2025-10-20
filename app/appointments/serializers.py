from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Staff, AppointmentRoom, AppointmentType, StaffAvailability,
    TimeSlot, Appointment, AppointmentCancellation, AppointmentReminder,
    AppointmentFeedback
)
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username', 'email']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff model"""
    user = UserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'id', 'user', 'role', 'role_display', 'title', 'bio',
            'specializations', 'room_number', 'phone_extension',
            'is_available', 'accepts_appointments', 'profile_image',
            'full_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentRoomSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentRoom model"""
    
    class Meta:
        model = AppointmentRoom
        fields = [
            'id', 'name', 'room_number', 'floor', 'capacity',
            'facilities', 'is_available', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentTypeSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentType model"""
    
    class Meta:
        model = AppointmentType
        fields = [
            'id', 'name', 'description', 'duration_minutes', 'price',
            'requires_preparation', 'preparation_instructions', 'is_active',
            'max_advance_booking_days', 'min_advance_booking_hours', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StaffAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for StaffAvailability model"""
    staff = StaffSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(), source='staff', write_only=True
    )
    appointment_types = AppointmentTypeSerializer(many=True, read_only=True)
    appointment_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentType.objects.all(), source='appointment_types',
        many=True, write_only=True
    )
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = StaffAvailability
        fields = [
            'id', 'staff', 'staff_id', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'appointment_types', 'appointment_type_ids',
            'is_available', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for TimeSlot model"""
    staff = StaffSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(), source='staff', write_only=True
    )
    appointment_type = AppointmentTypeSerializer(read_only=True)
    appointment_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentType.objects.all(), source='appointment_type',
        write_only=True, required=False
    )
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'staff', 'staff_id', 'date', 'start_time', 'end_time',
            'is_available', 'is_booked', 'appointment_type', 'appointment_type_id',
            'is_past', 'created_at'
        ]
        read_only_fields = ['id', 'is_past', 'created_at']
    
    def validate(self, data):
        """Validate time slot data"""
        if 'date' in data and 'start_time' in data:
            # Check if the time slot is in the past
            slot_datetime = datetime.combine(data['date'], data['start_time'])
            if timezone.make_aware(slot_datetime) < timezone.now():
                raise serializers.ValidationError("نمی‌توان برای زمان گذشته بازه زمانی ایجاد کرد.")
        
        if 'start_time' in data and 'end_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("زمان پایان باید بعد از زمان شروع باشد.")
        
        return data


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    client = UserSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='client', write_only=True, required=False
    )
    staff = StaffSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.filter(is_available=True, accepts_appointments=True),
        source='staff', write_only=True
    )
    appointment_type = AppointmentTypeSerializer(read_only=True)
    appointment_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentType.objects.filter(is_active=True),
        source='appointment_type', write_only=True
    )
    room = AppointmentRoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentRoom.objects.filter(is_available=True),
        source='room', write_only=True, required=False
    )
    time_slot = TimeSlotSerializer(read_only=True)
    time_slot_id = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.filter(is_available=True, is_booked=False),
        source='time_slot', write_only=True, required=False
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    confirmed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_id', 'staff', 'staff_id',
            'appointment_type', 'appointment_type_id', 'status', 'status_display',
            'date', 'start_time', 'end_time', 'time_slot', 'time_slot_id',
            'room', 'room_id', 'purpose', 'notes', 'internal_notes',
            'phone_number', 'alternative_phone', 'price', 'is_paid',
            'payment_method', 'transaction_id', 'confirmed_at', 'confirmed_by',
            'completed_at', 'arrival_time', 'departure_time', 'is_past',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status_display', 'is_past', 'confirmed_at', 'confirmed_by',
            'completed_at', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate appointment data"""
        # Set client to current user if not provided
        if not data.get('client') and self.context.get('request'):
            data['client'] = self.context['request'].user
        
        # Validate appointment date and time
        if 'date' in data and 'start_time' in data:
            appointment_datetime = datetime.combine(data['date'], data['start_time'])
            
            # Check if appointment is in the past
            if timezone.make_aware(appointment_datetime) < timezone.now():
                raise serializers.ValidationError("نمی‌توان برای زمان گذشته وقت ملاقات رزرو کرد.")
            
            # Check max advance booking
            if 'appointment_type' in data:
                max_days = data['appointment_type'].max_advance_booking_days
                if (data['date'] - timezone.now().date()).days > max_days:
                    raise serializers.ValidationError(
                        f"حداکثر {max_days} روز قبل می‌توان وقت رزرو کرد."
                    )
                
                # Check min advance booking
                min_hours = data['appointment_type'].min_advance_booking_hours
                hours_until = (appointment_datetime - datetime.now()).total_seconds() / 3600
                if hours_until < min_hours:
                    raise serializers.ValidationError(
                        f"حداقل {min_hours} ساعت قبل باید وقت رزرو شود."
                    )
        
        # Set end time based on appointment type duration
        if 'appointment_type' in data and 'start_time' in data:
            duration = data['appointment_type'].duration_minutes
            start_datetime = datetime.combine(data['date'], data['start_time'])
            end_datetime = start_datetime + timedelta(minutes=duration)
            data['end_time'] = end_datetime.time()
        
        # Set price from appointment type
        if 'appointment_type' in data:
            data['price'] = data['appointment_type'].price
        
        return data
    
    def create(self, validated_data):
        """Create appointment and update time slot if provided"""
        time_slot = validated_data.get('time_slot')
        if time_slot:
            time_slot.is_booked = True
            time_slot.save()
        
        return super().create(validated_data)


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating appointments by clients"""
    
    class Meta:
        model = Appointment
        fields = [
            'staff_id', 'appointment_type_id', 'date', 'start_time',
            'purpose', 'notes', 'phone_number', 'alternative_phone'
        ]
    
    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.filter(is_available=True, accepts_appointments=True),
        source='staff'
    )
    appointment_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AppointmentType.objects.filter(is_active=True),
        source='appointment_type'
    )


class AppointmentCancellationSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentCancellation model"""
    appointment = AppointmentSerializer(read_only=True)
    cancelled_by = UserSerializer(read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    
    class Meta:
        model = AppointmentCancellation
        fields = [
            'id', 'appointment', 'cancelled_by', 'reason', 'reason_display',
            'explanation', 'cancelled_at', 'refund_amount', 'is_refunded'
        ]
        read_only_fields = ['id', 'cancelled_at', 'cancelled_by']


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentReminder model"""
    appointment = AppointmentSerializer(read_only=True)
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    
    class Meta:
        model = AppointmentReminder
        fields = [
            'id', 'appointment', 'reminder_type', 'reminder_type_display',
            'scheduled_time', 'is_sent', 'sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for AppointmentFeedback model"""
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(status='completed'),
        source='appointment', write_only=True
    )
    
    class Meta:
        model = AppointmentFeedback
        fields = [
            'id', 'appointment', 'appointment_id', 'overall_rating',
            'staff_rating', 'facility_rating', 'waiting_time_rating',
            'comments', 'would_recommend', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_appointment_id(self, value):
        """Ensure feedback is only for user's own completed appointments"""
        request = self.context.get('request')
        if request and value.client != request.user:
            raise serializers.ValidationError("شما فقط می‌توانید برای ملاقات‌های خود بازخورد ثبت کنید.")
        
        # Check if feedback already exists
        if hasattr(value, 'feedback'):
            raise serializers.ValidationError("برای این ملاقات قبلاً بازخورد ثبت شده است.")
        
        return value


class AvailableSlotSerializer(serializers.Serializer):
    """Serializer for available appointment slots"""
    date = serializers.DateField()
    time = serializers.TimeField()
    staff = StaffSerializer()
    duration_minutes = serializers.IntegerField()
    is_available = serializers.BooleanField()