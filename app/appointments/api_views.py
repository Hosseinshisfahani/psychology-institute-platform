from rest_framework import generics, status, permissions, filters, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import (
    ClinicLocation, AppointmentType, TherapistSchedule, TherapistTimeOff,
    Appointment, AppointmentCancellation, AppointmentReschedule,
    CancellationPolicy, AppointmentReminder
)
from .serializers import (
    ClinicLocationSerializer, AppointmentTypeSerializer, TherapistScheduleSerializer,
    AppointmentSerializer, AppointmentListSerializer, AppointmentCreateSerializer,
    AppointmentCancellationSerializer, AppointmentRescheduleSerializer,
    CancellationPolicySerializer, AppointmentReminderSerializer,
    TherapistAvailabilitySerializer
)

User = get_user_model()


class AppointmentListAPIView(generics.ListCreateAPIView):
    """List and create appointments"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'therapist', 'appointment_type', 'location']
    search_fields = ['therapist__first_name', 'therapist__last_name', 'client__first_name', 'client__last_name']
    ordering_fields = ['scheduled_datetime', 'created_at']
    ordering = ['-scheduled_datetime']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentListSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'therapist':
            return Appointment.objects.filter(therapist=user).select_related(
                'client', 'therapist', 'appointment_type', 'location'
            )
        elif user.user_type == 'client':
            return Appointment.objects.filter(client=user).select_related(
                'client', 'therapist', 'appointment_type', 'location'
            )
        else:
            # Admin or staff can see all appointments
            return Appointment.objects.all().select_related(
                'client', 'therapist', 'appointment_type', 'location'
            )
    
    def perform_create(self, serializer):
        # Set client to current user if they are a client
        if self.request.user.user_type == 'client':
            serializer.save(client=self.request.user)
        else:
            serializer.save()


class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete appointment"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'therapist':
            return Appointment.objects.filter(therapist=user)
        elif user.user_type == 'client':
            return Appointment.objects.filter(client=user)
        else:
            return Appointment.objects.all()
    
    def perform_destroy(self, instance):
        # Instead of deleting, cancel the appointment
        instance.status = 'cancelled'
        instance.save()
        
        # Create cancellation record
        AppointmentCancellation.objects.create(
            appointment=instance,
            cancelled_by=self.request.user,
            reason="لغو توسط کاربر"
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user not in [appointment.client, appointment.therapist] and not request.user.is_staff:
        return Response({'error': 'شما مجاز به تغییر این نوبت نیستید'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AppointmentRescheduleSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                reschedule = serializer.save(
                    original_appointment=appointment,
                    rescheduled_by=request.user
                )
                return Response({
                    'message': 'نوبت با موفقیت تغییر زمان شد',
                    'new_appointment_id': reschedule.new_appointment.id
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user not in [appointment.client, appointment.therapist] and not request.user.is_staff:
        return Response({'error': 'شما مجاز به لغو این نوبت نیستید'}, status=status.HTTP_403_FORBIDDEN)
    
    if appointment.status in ['cancelled', 'completed']:
        return Response({'error': 'این نوبت قبلاً لغو یا تکمیل شده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = AppointmentCancellationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                cancellation = serializer.save(
                    appointment=appointment,
                    cancelled_by=request.user
                )
                return Response({
                    'message': 'نوبت با موفقیت لغو شد',
                    'cancellation_fee': float(cancellation.cancellation_fee),
                    'refund_amount': float(cancellation.refund_amount)
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TherapistListAPIView(APIView):
    """List available therapists"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        therapists = User.objects.filter(
            user_type='therapist',
            is_available=True,
            is_active=True
        ).select_related('profile')
        
        data = []
        for therapist in therapists:
            data.append({
                'id': therapist.id,
                'name': therapist.full_name,
                'specialization': therapist.specialization,
                'experience_years': therapist.experience_years,
                'hourly_rate': float(therapist.hourly_rate),
                'profile_image': therapist.profile_image.url if therapist.profile_image else None
            })
        return Response(data)


class TherapistAvailabilityAPIView(APIView):
    """Get therapist's available time slots"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, therapist_id):
        therapist = get_object_or_404(User, id=therapist_id, user_type='therapist')
        date = request.query_params.get('date')
        location_id = request.query_params.get('location_id')
        
        if not date:
            return Response({'error': 'تاریخ الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'فرمت تاریخ نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get available slots
        available_slots = self._get_available_slots(therapist, target_date, location_id)
        
        return Response({
            'therapist_id': therapist.id,
            'therapist_name': therapist.full_name,
            'date': target_date,
            'available_slots': available_slots
        })
    
    def _get_available_slots(self, therapist, target_date, location_id=None):
        """Calculate available time slots for a therapist on a specific date"""
        day_of_week = target_date.weekday()
        slots = []
        
        # Get therapist's schedule for this day
        schedules = TherapistSchedule.objects.filter(
            therapist=therapist,
            day_of_week=day_of_week,
            is_active=True
        )
        
        if location_id:
            schedules = schedules.filter(location_id=location_id)
        
        # Check if therapist is on time off
        time_off = TherapistTimeOff.objects.filter(
            therapist=therapist,
            start_date__lte=target_date,
            end_date__gte=target_date,
            is_approved=True
        ).exists()
        
        if time_off:
            return []
        
        # Generate time slots
        for schedule in schedules:
            current_time = datetime.combine(target_date, schedule.start_time)
            end_time = datetime.combine(target_date, schedule.end_time)
            
            while current_time + timedelta(minutes=60) <= end_time:
                # Check if this slot is available
                if self._is_slot_available(therapist, current_time, 60):
                    slots.append(current_time.isoformat())
                
                current_time += timedelta(minutes=15)  # 15-minute increments
        
        return slots
    
    def _is_slot_available(self, therapist, start_time, duration_minutes):
        """Check if a specific time slot is available"""
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check for overlapping appointments
        overlapping = Appointment.objects.filter(
            therapist=therapist,
            status__in=['scheduled', 'confirmed'],
            scheduled_datetime__lt=end_time
        ).exclude(
            scheduled_datetime__gte=end_time
        ).exists()
        
        return not overlapping


class AppointmentTypeListAPIView(generics.ListAPIView):
    """List appointment types"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentTypeSerializer
    queryset = AppointmentType.objects.filter(is_active=True)


class ClinicLocationListAPIView(generics.ListAPIView):
    """List clinic locations"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClinicLocationSerializer
    queryset = ClinicLocation.objects.filter(is_active=True)


class CancellationPolicyListAPIView(generics.ListAPIView):
    """List cancellation policies"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CancellationPolicySerializer
    queryset = CancellationPolicy.objects.filter(is_active=True)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_statistics(request):
    """Get appointment statistics for dashboard"""
    user = request.user
    
    if user.user_type == 'therapist':
        appointments = Appointment.objects.filter(therapist=user)
    elif user.user_type == 'client':
        appointments = Appointment.objects.filter(client=user)
    else:
        appointments = Appointment.objects.all()
    
    stats = {
        'total_appointments': appointments.count(),
        'scheduled': appointments.filter(status='scheduled').count(),
        'confirmed': appointments.filter(status='confirmed').count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
        'upcoming': appointments.filter(
            status__in=['scheduled', 'confirmed'],
            scheduled_datetime__gte=timezone.now()
        ).count()
    }
    
    return Response(stats)
