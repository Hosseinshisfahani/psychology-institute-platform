from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, date
import jdatetime

from .models import (
    AppointmentType, Specialist, TimeSlot, Appointment,
    AppointmentReminder, WaitingList
)
from .serializers import (
    AppointmentTypeSerializer, SpecialistSerializer, TimeSlotSerializer,
    AppointmentSerializer, AppointmentCreateSerializer, AppointmentReminderSerializer,
    WaitingListSerializer, AvailableSlotSerializer
)


# Appointment Types
class AppointmentTypeListAPIView(generics.ListAPIView):
    """List all active appointment types"""
    queryset = AppointmentType.objects.filter(is_active=True)
    serializer_class = AppointmentTypeSerializer
    permission_classes = [IsAuthenticated]


class AppointmentTypeDetailAPIView(generics.RetrieveAPIView):
    """Get appointment type details"""
    queryset = AppointmentType.objects.filter(is_active=True)
    serializer_class = AppointmentTypeSerializer
    permission_classes = [IsAuthenticated]


# Specialists
class SpecialistListAPIView(generics.ListAPIView):
    """List all available specialists"""
    queryset = Specialist.objects.filter(is_available=True)
    serializer_class = SpecialistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'specialization']


class SpecialistDetailAPIView(generics.RetrieveAPIView):
    """Get specialist details"""
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    permission_classes = [IsAuthenticated]


# Time Slots
class TimeSlotListAPIView(generics.ListAPIView):
    """List time slots, optionally filtered by specialist"""
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TimeSlot.objects.filter(is_available=True)
        specialist_id = self.request.query_params.get('specialist')
        if specialist_id:
            queryset = queryset.filter(specialist_id=specialist_id)
        return queryset.order_by('day_of_week', 'start_time')


# Appointments
class AppointmentListAPIView(generics.ListCreateAPIView):
    """List user's appointments or create new appointment"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['appointment_date', 'created_at']
    ordering = ['-appointment_date', '-appointment_time']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.filter(client=user)


class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or cancel appointment"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.filter(client=user)
    
    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()
        if appointment.status == 'confirmed':
            # Don't delete, just mark as cancelled
            appointment.status = 'cancelled'
            appointment.cancelled_at = timezone.now()
            appointment.save()
            return Response(
                {'message': 'Appointment cancelled successfully'},
                status=status.HTTP_200_OK
            )
        return super().destroy(request, *args, **kwargs)


# Available Slots
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_slots(request):
    """Get available appointment slots for a specific date range"""
    
    # Get parameters
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    appointment_type_id = request.query_params.get('appointment_type')
    specialist_id = request.query_params.get('specialist')
    
    if not all([start_date, end_date, appointment_type_id]):
        return Response(
            {'error': 'start_date, end_date, and appointment_type are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        appointment_type = AppointmentType.objects.get(id=appointment_type_id)
    except (ValueError, AppointmentType.DoesNotExist):
        return Response(
            {'error': 'Invalid date format or appointment type'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get time slots
    time_slots = TimeSlot.objects.filter(is_available=True)
    if specialist_id:
        time_slots = time_slots.filter(specialist_id=specialist_id)
    elif appointment_type.requires_specialist:
        return Response(
            {'error': 'This appointment type requires a specialist'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate available slots
    available_slots = []
    current_date = start_date
    
    while current_date <= end_date:
        day_of_week = current_date.weekday()
        # Convert Python weekday (0=Monday) to our system (0=Saturday)
        day_of_week = (day_of_week + 2) % 7
        
        day_slots = time_slots.filter(day_of_week=day_of_week)
        
        for slot in day_slots:
            # Check existing appointments
            existing_count = Appointment.objects.filter(
                appointment_date=current_date,
                appointment_time=slot.start_time,
                specialist=slot.specialist,
                status__in=['pending', 'confirmed']
            ).count()
            
            if existing_count < slot.max_appointments:
                available_slots.append({
                    'date': current_date,
                    'time': slot.start_time,
                    'specialist': slot.specialist,
                    'available_count': slot.max_appointments - existing_count
                })
        
        current_date += timedelta(days=1)
    
    serializer = AvailableSlotSerializer(available_slots, many=True)
    return Response(serializer.data)


# Appointment Actions
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_appointment(request, appointment_id):
    """Confirm a pending appointment (admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Only staff can confirm appointments'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'pending':
        return Response(
            {'error': 'Only pending appointments can be confirmed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    appointment.status = 'confirmed'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Create reminder
    reminder_time = datetime.combine(
        appointment.appointment_date,
        appointment.appointment_time
    ) - timedelta(hours=24)
    
    AppointmentReminder.objects.create(
        appointment=appointment,
        reminder_type='sms',
        scheduled_time=timezone.make_aware(reminder_time)
    )
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if not (request.user.is_staff or appointment.client == request.user):
        return Response(
            {'error': 'You do not have permission to cancel this appointment'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if appointment.status in ['completed', 'cancelled']:
        return Response(
            {'error': 'This appointment cannot be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    appointment.status = 'cancelled'
    appointment.cancelled_at = timezone.now()
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_appointment_complete(request, appointment_id):
    """Mark appointment as completed (admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Only staff can mark appointments as complete'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'confirmed':
        return Response(
            {'error': 'Only confirmed appointments can be marked as complete'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    appointment.status = 'completed'
    appointment.completed_at = timezone.now()
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


# Waiting List
class WaitingListCreateAPIView(generics.CreateAPIView):
    """Add to waiting list"""
    serializer_class = WaitingListSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class WaitingListListAPIView(generics.ListAPIView):
    """List user's waiting list entries"""
    serializer_class = WaitingListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WaitingList.objects.filter(
            client=self.request.user,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_waiting_list(request, waiting_list_id):
    """Remove from waiting list"""
    entry = get_object_or_404(
        WaitingList,
        id=waiting_list_id,
        client=request.user
    )
    entry.is_active = False
    entry.save()
    
    return Response({'message': 'Removed from waiting list'})


# Statistics (Admin)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def appointment_statistics(request):
    """Get appointment statistics for admin dashboard"""
    
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).aggregate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(status='confirmed')),
        pending=Count('id', filter=Q(status='pending')),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled')),
        no_show=Count('id', filter=Q(status='no_show'))
    )
    
    # This month's appointments
    month_appointments = Appointment.objects.filter(
        appointment_date__gte=start_of_month,
        appointment_date__lte=today
    ).aggregate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(status='confirmed')),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled'))
    )
    
    # Waiting list
    waiting_list_count = WaitingList.objects.filter(is_active=True).count()
    
    # Available specialists
    available_specialists = Specialist.objects.filter(is_available=True).count()
    
    return Response({
        'today': today_appointments,
        'this_month': month_appointments,
        'waiting_list': waiting_list_count,
        'available_specialists': available_specialists
    })