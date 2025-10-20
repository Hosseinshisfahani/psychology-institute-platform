from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AppointmentType, Specialist, TimeSlot, Appointment, 
    AppointmentReminder, WaitingList
)
import jdatetime

User = get_user_model()


class AppointmentTypeSerializer(serializers.ModelSerializer):
    """Serializer for appointment types"""
    
    class Meta:
        model = AppointmentType
        fields = [
            'id', 'name', 'description', 'duration_minutes', 
            'price', 'requires_specialist', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SpecialistSerializer(serializers.ModelSerializer):
    """Serializer for specialists"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    
    class Meta:
        model = Specialist
        fields = [
            'id', 'user', 'user_name', 'user_email', 'specialization',
            'specialization_display', 'bio', 'education', 'certifications',
            'experience_years', 'room_number', 'is_available', 'profile_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for time slots"""
    
    specialist_name = serializers.CharField(source='specialist.user.get_full_name', read_only=True)
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'specialist', 'specialist_name', 'day_of_week', 
            'day_display', 'start_time', 'end_time', 'is_available',
            'max_appointments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments"""
    
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    appointment_type_name = serializers.CharField(source='appointment_type.name', read_only=True)
    specialist_name = serializers.CharField(source='specialist.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    appointment_date_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_number', 'client', 'client_name', 'client_email',
            'appointment_type', 'appointment_type_name', 'specialist', 'specialist_name',
            'status', 'status_display', 'appointment_date', 'appointment_date_persian',
            'appointment_time', 'duration_minutes', 'room_number', 'client_phone',
            'emergency_contact', 'reason_for_visit', 'notes', 'price', 'is_paid',
            'payment_method', 'created_at', 'updated_at', 'confirmed_at',
            'completed_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'appointment_number', 'created_at', 'updated_at',
            'confirmed_at', 'completed_at', 'cancelled_at'
        ]
    
    def get_appointment_date_persian(self, obj):
        if obj.appointment_date:
            return jdatetime.date.fromgregorian(date=obj.appointment_date).strftime('%Y/%m/%d')
        return None


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'appointment_type', 'specialist', 'appointment_date',
            'appointment_time', 'client_phone', 'emergency_contact',
            'reason_for_visit', 'notes'
        ]
    
    def create(self, validated_data):
        # Set client from request user
        validated_data['client'] = self.context['request'].user
        
        # Get duration and price from appointment type
        appointment_type = validated_data['appointment_type']
        validated_data['duration_minutes'] = appointment_type.duration_minutes
        validated_data['price'] = appointment_type.price
        
        # Set room number from specialist if available
        if validated_data.get('specialist'):
            validated_data['room_number'] = validated_data['specialist'].room_number
        
        return super().create(validated_data)


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """Serializer for appointment reminders"""
    
    appointment_number = serializers.CharField(source='appointment.appointment_number', read_only=True)
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    
    class Meta:
        model = AppointmentReminder
        fields = [
            'id', 'appointment', 'appointment_number', 'reminder_type',
            'reminder_type_display', 'scheduled_time', 'is_sent', 'sent_at',
            'created_at'
        ]
        read_only_fields = ['id', 'is_sent', 'sent_at', 'created_at']


class WaitingListSerializer(serializers.ModelSerializer):
    """Serializer for waiting list entries"""
    
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    appointment_type_name = serializers.CharField(source='appointment_type.name', read_only=True)
    specialist_name = serializers.CharField(source='specialist.user.get_full_name', read_only=True)
    
    class Meta:
        model = WaitingList
        fields = [
            'id', 'client', 'client_name', 'appointment_type', 'appointment_type_name',
            'specialist', 'specialist_name', 'preferred_days', 'preferred_time_start',
            'preferred_time_end', 'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AvailableSlotSerializer(serializers.Serializer):
    """Serializer for available appointment slots"""
    
    date = serializers.DateField()
    time = serializers.TimeField()
    specialist = SpecialistSerializer(read_only=True)
    available_count = serializers.IntegerField()
    
    class Meta:
        fields = ['date', 'time', 'specialist', 'available_count']