from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    ClinicLocation, AppointmentType, TherapistSchedule, TherapistTimeOff,
    Appointment, AppointmentCancellation, AppointmentReschedule,
    CancellationPolicy, AppointmentReminder
)

User = get_user_model()


class ClinicLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicLocation
        fields = ['id', 'name', 'address', 'city', 'phone', 'capacity', 'facilities', 'is_active']
        read_only_fields = ['id']


class AppointmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentType
        fields = ['id', 'name', 'description', 'default_duration_minutes', 'price', 'color', 'is_active']
        read_only_fields = ['id']


class TherapistScheduleSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source='therapist.full_name', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = TherapistSchedule
        fields = [
            'id', 'therapist', 'therapist_name', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'location', 'location_name', 'is_active'
        ]
        read_only_fields = ['id']


class TherapistTimeOffSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source='therapist.full_name', read_only=True)
    
    class Meta:
        model = TherapistTimeOff
        fields = [
            'id', 'therapist', 'therapist_name', 'start_date', 'end_date',
            'reason', 'is_approved'
        ]
        read_only_fields = ['id']


class AppointmentListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    therapist_name = serializers.CharField(source='therapist.full_name', read_only=True)
    appointment_type_name = serializers.CharField(source='appointment_type.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'therapist', 'therapist_name',
            'appointment_type', 'appointment_type_name', 'location', 'location_name',
            'scheduled_datetime', 'duration_minutes', 'status', 'status_display',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    therapist_name = serializers.CharField(source='therapist.full_name', read_only=True)
    appointment_type_name = serializers.CharField(source='appointment_type.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    end_datetime = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'therapist', 'therapist_name',
            'appointment_type', 'appointment_type_name', 'location', 'location_name',
            'scheduled_datetime', 'end_datetime', 'duration_minutes', 'status', 
            'status_display', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'therapist', 'appointment_type', 'location',
            'scheduled_datetime', 'duration_minutes', 'notes'
        ]
    
    def validate(self, data):
        # Check if therapist is available
        therapist = data['therapist']
        scheduled_datetime = data['scheduled_datetime']
        duration_minutes = data['duration_minutes']
        
        # Check if therapist is available at this time
        if not self._is_therapist_available(therapist, scheduled_datetime, duration_minutes):
            raise serializers.ValidationError("درمانگر در این زمان در دسترس نیست")
        
        # Check for overlapping appointments
        if self._has_overlapping_appointment(therapist, scheduled_datetime, duration_minutes):
            raise serializers.ValidationError("این زمان قبلاً رزرو شده است")
        
        # Check minimum advance booking (1 hour)
        if scheduled_datetime <= timezone.now() + timedelta(hours=1):
            raise serializers.ValidationError("نوبت باید حداقل یک ساعت قبل رزرو شود")
        
        return data
    
    def _is_therapist_available(self, therapist, scheduled_datetime, duration_minutes):
        """Check if therapist is available based on schedule and time off"""
        # Check if therapist has schedule for this day
        day_of_week = scheduled_datetime.weekday()
        start_time = scheduled_datetime.time()
        end_time = (scheduled_datetime + timedelta(minutes=duration_minutes)).time()
        
        # Check regular schedule
        schedule = TherapistSchedule.objects.filter(
            therapist=therapist,
            day_of_week=day_of_week,
            is_active=True
        ).first()
        
        if not schedule:
            return False
        
        if not (schedule.start_time <= start_time and end_time <= schedule.end_time):
            return False
        
        # Check time off
        date = scheduled_datetime.date()
        time_off = TherapistTimeOff.objects.filter(
            therapist=therapist,
            start_date__lte=date,
            end_date__gte=date,
            is_approved=True
        ).exists()
        
        return not time_off
    
    def _has_overlapping_appointment(self, therapist, scheduled_datetime, duration_minutes):
        """Check if there's an overlapping appointment"""
        end_datetime = scheduled_datetime + timedelta(minutes=duration_minutes)
        
        # Get all existing appointments for this therapist
        existing_appointments = Appointment.objects.filter(
            therapist=therapist,
            status__in=['scheduled', 'confirmed']
        )
        
        # Check for overlaps manually
        for appointment in existing_appointments:
            existing_end = appointment.scheduled_datetime + timedelta(minutes=appointment.duration_minutes)
            
            # Check if appointments overlap
            if (scheduled_datetime < existing_end and 
                end_datetime > appointment.scheduled_datetime):
                return True
        
        return False


class AppointmentCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentCancellation
        fields = ['reason']
    
    def create(self, validated_data):
        # Get appointment and cancelled_by from the context passed by the view
        appointment = self.context.get('appointment')
        cancelled_by = self.context.get('cancelled_by')
        reason = validated_data['reason']
        
        # Create cancellation record without fees
        cancellation = AppointmentCancellation.objects.create(
            appointment=appointment,
            cancelled_by=cancelled_by,
            reason=reason,
            cancellation_fee=0,
            refund_amount=0
        )
        
        # Update appointment status
        appointment.status = 'cancelled'
        appointment.save()
        
        return cancellation


class AppointmentRescheduleSerializer(serializers.ModelSerializer):
    new_scheduled_datetime = serializers.DateTimeField(write_only=True)
    new_duration_minutes = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = AppointmentReschedule
        fields = ['original_appointment', 'rescheduled_by', 'reason', 'new_scheduled_datetime', 'new_duration_minutes']
    
    def create(self, validated_data):
        original_appointment = validated_data['original_appointment']
        rescheduled_by = validated_data['rescheduled_by']
        reason = validated_data['reason']
        new_scheduled_datetime = validated_data['new_scheduled_datetime']
        new_duration_minutes = validated_data.get('new_duration_minutes', original_appointment.duration_minutes)
        
        # Create new appointment
        new_appointment = Appointment.objects.create(
            client=original_appointment.client,
            therapist=original_appointment.therapist,
            appointment_type=original_appointment.appointment_type,
            location=original_appointment.location,
            scheduled_datetime=new_scheduled_datetime,
            duration_minutes=new_duration_minutes,
            status='scheduled',
            notes=original_appointment.notes
        )
        
        # Create reschedule record
        reschedule = AppointmentReschedule.objects.create(
            original_appointment=original_appointment,
            new_appointment=new_appointment,
            rescheduled_by=rescheduled_by,
            reason=reason
        )
        
        # Update original appointment status
        original_appointment.status = 'rescheduled'
        original_appointment.save()
        
        return reschedule


class CancellationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationPolicy
        fields = ['id', 'name', 'hours_before_appointment', 'cancellation_fee_percentage', 'description', 'is_active']
        read_only_fields = ['id']


class AppointmentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentReminder
        fields = ['id', 'appointment', 'reminder_type', 'scheduled_time', 'status', 'sent_at']
        read_only_fields = ['id', 'sent_at']


class TherapistAvailabilitySerializer(serializers.Serializer):
    """Serializer for therapist availability slots"""
    therapist_id = serializers.IntegerField()
    therapist_name = serializers.CharField()
    available_slots = serializers.ListField(
        child=serializers.DateTimeField()
    )
    location = ClinicLocationSerializer()
