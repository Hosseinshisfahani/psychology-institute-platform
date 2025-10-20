from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    ClinicLocation, AppointmentType, TherapistSchedule, Appointment,
    CancellationPolicy, AppointmentCancellation
)

User = get_user_model()


class AppointmentModelTest(TestCase):
    def setUp(self):
        # Create test users
        self.client_user = User.objects.create_user(
            email='client@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Client',
            user_type='client'
        )
        
        self.therapist_user = User.objects.create_user(
            email='therapist@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Therapist',
            user_type='therapist',
            specialization='Clinical Psychology',
            is_available=True
        )
        
        # Create test location
        self.location = ClinicLocation.objects.create(
            name='Test Clinic',
            address='Test Address',
            city='Test City',
            phone='1234567890'
        )
        
        # Create appointment type
        self.appointment_type = AppointmentType.objects.create(
            name='Individual Therapy',
            default_duration_minutes=60,
            price=100.00
        )
        
        # Create therapist schedule
        self.schedule = TherapistSchedule.objects.create(
            therapist=self.therapist_user,
            day_of_week=0,  # Monday
            start_time='09:00',
            end_time='17:00',
            location=self.location
        )
    
    def test_appointment_creation(self):
        """Test creating an appointment"""
        appointment = Appointment.objects.create(
            client=self.client_user,
            therapist=self.therapist_user,
            appointment_type=self.appointment_type,
            location=self.location,
            scheduled_datetime=timezone.now() + timedelta(days=1),
            duration_minutes=60
        )
        
        self.assertEqual(appointment.client, self.client_user)
        self.assertEqual(appointment.therapist, self.therapist_user)
        self.assertEqual(appointment.status, 'scheduled')
    
    def test_appointment_end_datetime(self):
        """Test appointment end datetime calculation"""
        start_time = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(
            client=self.client_user,
            therapist=self.therapist_user,
            appointment_type=self.appointment_type,
            location=self.location,
            scheduled_datetime=start_time,
            duration_minutes=90
        )
        
        expected_end = start_time + timedelta(minutes=90)
        self.assertEqual(appointment.end_datetime, expected_end)
    
    def test_cancellation_fee_calculation(self):
        """Test cancellation fee calculation"""
        # Create cancellation policy
        policy = CancellationPolicy.objects.create(
            name='24 Hour Policy',
            hours_before_appointment=24,
            cancellation_fee_percentage=0.0,
            description='Free cancellation 24+ hours before'
        )
        
        # Create appointment
        appointment = Appointment.objects.create(
            client=self.client_user,
            therapist=self.therapist_user,
            appointment_type=self.appointment_type,
            location=self.location,
            scheduled_datetime=timezone.now() + timedelta(hours=25),
            duration_minutes=60
        )
        
        # Create cancellation
        cancellation = AppointmentCancellation.objects.create(
            appointment=appointment,
            cancelled_by=self.client_user,
            reason='Test cancellation'
        )
        
        # Should be free cancellation (25 hours > 24 hours)
        self.assertEqual(cancellation.cancellation_fee, 0)
        self.assertEqual(cancellation.refund_amount, 100.00)
