from rest_framework import serializers
from .models import Therapist, Session, SessionType, SessionBooking
from django.contrib.auth import get_user_model
import jdatetime

User = get_user_model()

class TherapistSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    experience_years = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    total_sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = Therapist
        fields = [
            'id', 'user', 'full_name', 'specialization', 'specialization_display',
            'bio', 'education', 'certifications', 'experience_years',
            'hourly_rate', 'rating', 'total_sessions', 'is_available',
            'profile_image', 'created_at'
        ]
    
    def get_experience_years(self, obj):
        if obj.experience_start_date:
            from datetime import date
            today = date.today()
            return today.year - obj.experience_start_date.year
        return 0
    
    def get_rating(self, obj):
        # Calculate average rating from completed sessions
        completed_sessions = Session.objects.filter(
            therapist=obj,
            status='completed',
            rating__isnull=False
        )
        if completed_sessions.exists():
            return round(completed_sessions.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating'], 1)
        return 0.0
    
    def get_total_sessions(self, obj):
        return Session.objects.filter(therapist=obj, status='completed').count()

class SessionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionType
        fields = ['id', 'name', 'description', 'duration', 'price', 'is_available']

class SessionBookingSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source='therapist.get_full_name', read_only=True)
    session_type_name = serializers.CharField(source='session_type.name', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionBooking
        fields = [
            'id', 'user', 'therapist', 'therapist_name', 'session_type', 'session_type_name',
            'preferred_date', 'preferred_time', 'duration', 'notes', 'status',
            'created_at', 'created_at_persian'
        ]
        read_only_fields = ['user', 'created_at']
    
    def get_created_at_persian(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None

class SessionSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source='therapist.get_full_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    session_type_name = serializers.CharField(source='session_type.name', read_only=True)
    start_time_persian = serializers.SerializerMethodField()
    end_time_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = [
            'id', 'user', 'user_name', 'therapist', 'therapist_name',
            'session_type', 'session_type_name', 'start_time', 'end_time',
            'start_time_persian', 'end_time_persian', 'status', 'notes',
            'rating', 'feedback', 'created_at'
        ]
    
    def get_start_time_persian(self, obj):
        if obj.start_time:
            return jdatetime.datetime.fromgregorian(datetime=obj.start_time).strftime('%Y/%m/%d %H:%M')
        return None
    
    def get_end_time_persian(self, obj):
        if obj.end_time:
            return jdatetime.datetime.fromgregorian(datetime=obj.end_time).strftime('%Y/%m/%d %H:%M')
        return None

class SessionRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['rating', 'feedback']
    
    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("امتیاز باید بین 1 تا 5 باشد")
        return value
