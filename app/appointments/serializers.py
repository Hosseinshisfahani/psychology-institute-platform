from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Staff, Room, AppointmentType, TimeSlot, Appointment,
    AppointmentCancellation, AppointmentReminder, AppointmentFeedback
)
import jdatetime

User = get_user_model()


class StaffSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'id', 'user', 'user_name', 'user_email', 'role', 'role_display',
            'title', 'bio', 'is_available', 'can_accept_appointments',
            'office_location', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RoomSerializer(serializers.ModelSerializer):
    location_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'building', 'floor', 'capacity', 'facilities',
            'is_available', 'location_display', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_location_display(self, obj):
        return str(obj)


class AppointmentTypeSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AppointmentType
        fields = [
            'id', 'name', 'description', 'duration_minutes', 'duration_display',
            'requires_approval', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه" if minutes > 0 else f"{hours} ساعت"
        return f"{minutes} دقیقه"


class TimeSlotSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True, allow_null=True)
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'staff', 'staff_name', 'day_of_week', 'day_display',
            'start_time', 'end_time', 'is_available', 'max_appointments',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    appointment_type_name = serializers.CharField(source='appointment_type.name', read_only=True)
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True, allow_null=True)
    room_name = serializers.CharField(source='room.name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    appointment_date_persian = serializers.SerializerMethodField()
    end_time = serializers.TimeField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'user_name', 'user_email', 'appointment_type',
            'appointment_type_name', 'staff', 'staff_name', 'room', 'room_name',
            'status', 'status_display', 'appointment_date', 'appointment_date_persian',
            'appointment_time', 'end_time', 'duration_minutes', 'purpose', 'notes',
            'confirmed_by', 'confirmed_at', 'confirmation_notes', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'confirmed_by', 'confirmed_at', 'created_at', 'updated_at', 'completed_at', 'end_time']
    
    def get_appointment_date_persian(self, obj):
        if obj.appointment_date:
            return jdatetime.datetime.fromgregorian(datetime=obj.appointment_date).strftime('%Y/%m/%d')
        return None
    
    def validate(self, data):
        # Validate appointment doesn't conflict with existing appointments
        if 'appointment_date' in data and 'appointment_time' in data:
            conflicts = Appointment.objects.filter(
                staff=data.get('staff'),
                appointment_date=data['appointment_date'],
                appointment_time=data['appointment_time'],
                status__in=['confirmed', 'pending']
            )
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            if conflicts.exists():
                raise serializers.ValidationError("این زمان قبلاً رزرو شده است.")
        
        return data


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments by users"""
    class Meta:
        model = Appointment
        fields = [
            'appointment_type', 'appointment_date', 'appointment_time',
            'purpose', 'notes'
        ]
    
    def create(self, validated_data):
        # Set duration from appointment type
        appointment_type = validated_data['appointment_type']
        validated_data['duration_minutes'] = appointment_type.duration_minutes
        
        # Set user from request
        validated_data['user'] = self.context['request'].user
        
        return super().create(validated_data)


class AppointmentCancellationSerializer(serializers.ModelSerializer):
    cancelled_by_name = serializers.CharField(source='cancelled_by.get_full_name', read_only=True)
    
    class Meta:
        model = AppointmentCancellation
        fields = [
            'id', 'appointment', 'cancelled_by', 'cancelled_by_name',
            'reason', 'cancelled_at'
        ]
        read_only_fields = ['id', 'cancelled_at']


class AppointmentReminderSerializer(serializers.ModelSerializer):
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    
    class Meta:
        model = AppointmentReminder
        fields = [
            'id', 'appointment', 'reminder_type', 'reminder_type_display',
            'scheduled_time', 'is_sent', 'sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'is_sent', 'sent_at', 'created_at']


class AppointmentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentFeedback
        fields = [
            'id', 'appointment', 'overall_rating', 'staff_rating',
            'location_rating', 'comments', 'would_recommend', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# Admin serializers with more details
class AdminAppointmentSerializer(AppointmentSerializer):
    """Extended serializer for admin panel with internal notes"""
    confirmed_by_name = serializers.CharField(source='confirmed_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + [
            'internal_notes', 'confirmed_by_name'
        ]


class AdminStaffSerializer(StaffSerializer):
    """Extended serializer for admin panel"""
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    appointments_count = serializers.SerializerMethodField()
    
    class Meta(StaffSerializer.Meta):
        fields = StaffSerializer.Meta.fields + [
            'user_phone', 'appointments_count'
        ]
    
    def get_appointments_count(self, obj):
        return obj.appointments.count()