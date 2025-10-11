from rest_framework import serializers
from .models import (
    Cohort, CohortSession, CohortEnrollment, 
    CohortInstallment, CohortAttendance
)


class CohortSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    available_spots = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Cohort
        fields = [
            'id', 'title', 'description', 'instructor_name',
            'start_date', 'end_date', 'class_time', 'duration_minutes',
            'full_price', 'installment_3_price', 'installment_6_price',
            'max_students', 'current_enrollments', 'available_spots',
            'is_full', 'status', 'created_at'
        ]


class CohortDetailSerializer(CohortSerializer):
    sessions = serializers.SerializerMethodField()
    
    class Meta(CohortSerializer.Meta):
        fields = CohortSerializer.Meta.fields + ['sessions']
    
    def get_sessions(self, obj):
        sessions = obj.sessions.all().order_by('session_number')
        return CohortSessionSerializer(sessions, many=True).data


class CohortSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CohortSession
        fields = [
            'id', 'session_number', 'title', 'description',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'is_completed', 'is_recording_available', 'recording_url'
        ]


class CohortEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    cohort_title = serializers.CharField(source='cohort.title', read_only=True)
    
    class Meta:
        model = CohortEnrollment
        fields = [
            'id', 'student_name', 'cohort_title', 'status',
            'payment_type', 'payment_status', 'total_amount',
            'amount_paid', 'remaining_amount', 'enrolled_at'
        ]


class CohortInstallmentSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = CohortInstallment
        fields = [
            'id', 'installment_number', 'amount', 'due_date',
            'status', 'paid_at', 'payment_method', 'transaction_id',
            'is_overdue'
        ]


class CohortAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='enrollment.student.full_name', read_only=True)
    
    class Meta:
        model = CohortAttendance
        fields = [
            'id', 'student_name', 'is_present', 'arrived_at',
            'left_at', 'notes'
        ]
