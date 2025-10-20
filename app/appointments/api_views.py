from rest_framework import generics, status, filters, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import (
    Staff, AppointmentRoom, AppointmentType, StaffAvailability,
    TimeSlot, Appointment, AppointmentCancellation, AppointmentReminder,
    AppointmentFeedback
)
from .serializers import (
    StaffSerializer, AppointmentRoomSerializer, AppointmentTypeSerializer,
    StaffAvailabilitySerializer, TimeSlotSerializer, AppointmentSerializer,
    AppointmentCreateSerializer, AppointmentCancellationSerializer,
    AppointmentReminderSerializer, AppointmentFeedbackSerializer,
    AvailableSlotSerializer
)


class StaffListAPIView(generics.ListAPIView):
    """List all available staff members who accept appointments"""
    queryset = Staff.objects.filter(is_available=True, accepts_appointments=True)
    serializer_class = StaffSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'specializations', 'title']
    ordering_fields = ['user__first_name', 'user__last_name', 'role']
    ordering = ['user__first_name']


class StaffDetailAPIView(generics.RetrieveAPIView):
    """Get staff member details"""
    queryset = Staff.objects.filter(is_available=True, accepts_appointments=True)
    serializer_class = StaffSerializer
    permission_classes = [AllowAny]


class AppointmentTypeListAPIView(generics.ListAPIView):
    """List all active appointment types"""
    queryset = AppointmentType.objects.filter(is_active=True)
    serializer_class = AppointmentTypeSerializer
    permission_classes = [AllowAny]
    ordering = ['name']


class AppointmentRoomListAPIView(generics.ListAPIView):
    """List all available appointment rooms"""
    queryset = AppointmentRoom.objects.filter(is_available=True)
    serializer_class = AppointmentRoomSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['floor', 'room_number']


class MyAppointmentListAPIView(generics.ListAPIView):
    """List user's appointments"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'start_time', 'created_at']
    ordering = ['-date', '-start_time']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(client=user)
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by date range
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
        
        return queryset.select_related('staff__user', 'appointment_type', 'room')


class AppointmentDetailAPIView(generics.RetrieveAPIView):
    """Get appointment details"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own appointments
        return Appointment.objects.filter(client=self.request.user)


class CreateAppointmentAPIView(generics.CreateAPIView):
    """Create a new appointment"""
    serializer_class = AppointmentCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user, status='pending')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_slots(request):
    """Get available appointment slots for a specific staff and date range"""
    staff_id = request.query_params.get('staff_id')
    appointment_type_id = request.query_params.get('appointment_type_id')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    
    if not all([staff_id, appointment_type_id, from_date]):
        return Response(
            {'error': 'staff_id, appointment_type_id, and from_date are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        staff = Staff.objects.get(id=staff_id, is_available=True, accepts_appointments=True)
        appointment_type = AppointmentType.objects.get(id=appointment_type_id, is_active=True)
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        else:
            to_date = from_date + timedelta(days=7)  # Default to 1 week
        
    except Staff.DoesNotExist:
        return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
    except AppointmentType.DoesNotExist:
        return Response({'error': 'Appointment type not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get staff availability for the date range
    available_slots = []
    current_date = from_date
    
    while current_date <= to_date:
        # Skip past dates
        if current_date < timezone.now().date():
            current_date += timedelta(days=1)
            continue
        
        # Get day of week (0=Saturday in our system)
        day_of_week = (current_date.weekday() + 2) % 7  # Convert Python's Monday=0 to our Saturday=0
        
        # Get staff availability for this day
        availabilities = StaffAvailability.objects.filter(
            staff=staff,
            day_of_week=day_of_week,
            is_available=True,
            appointment_types=appointment_type
        )
        
        for availability in availabilities:
            # Generate time slots based on appointment duration
            slot_start = datetime.combine(current_date, availability.start_time)
            slot_end = datetime.combine(current_date, availability.end_time)
            duration = timedelta(minutes=appointment_type.duration_minutes)
            
            while slot_start + duration <= slot_end:
                # Check if slot is already booked
                is_booked = Appointment.objects.filter(
                    staff=staff,
                    date=current_date,
                    start_time=slot_start.time(),
                    status__in=['pending', 'confirmed']
                ).exists()
                
                # Check if time slot exists and is available
                time_slot = TimeSlot.objects.filter(
                    staff=staff,
                    date=current_date,
                    start_time=slot_start.time()
                ).first()
                
                if not is_booked and (not time_slot or time_slot.is_available):
                    # Check minimum advance booking
                    hours_until = (slot_start - datetime.now()).total_seconds() / 3600
                    if hours_until >= appointment_type.min_advance_booking_hours:
                        available_slots.append({
                            'date': current_date,
                            'time': slot_start.time(),
                            'staff': StaffSerializer(staff).data,
                            'duration_minutes': appointment_type.duration_minutes,
                            'is_available': True
                        })
                
                slot_start += duration
        
        current_date += timedelta(days=1)
    
    serializer = AvailableSlotSerializer(available_slots, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id, client=request.user)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if appointment.status in ['completed', 'cancelled']:
        return Response(
            {'error': 'Cannot cancel completed or already cancelled appointments'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if appointment is too close (less than 24 hours)
    appointment_datetime = datetime.combine(appointment.date, appointment.start_time)
    hours_until = (timezone.make_aware(appointment_datetime) - timezone.now()).total_seconds() / 3600
    
    if hours_until < 24:
        return Response(
            {'error': 'Cannot cancel appointments less than 24 hours in advance'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reason = request.data.get('reason', '')
    appointment.cancel(reason)
    
    # Create cancellation record
    cancellation = AppointmentCancellation.objects.create(
        appointment=appointment,
        cancelled_by=request.user,
        reason='client_request',
        explanation=reason
    )
    
    serializer = AppointmentCancellationSerializer(cancellation)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id, client=request.user)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if appointment.status not in ['pending', 'confirmed']:
        return Response(
            {'error': 'Can only reschedule pending or confirmed appointments'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    new_date = request.data.get('date')
    new_time = request.data.get('start_time')
    
    if not new_date or not new_time:
        return Response(
            {'error': 'Both date and start_time are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        new_date = datetime.strptime(new_date, '%Y-%m-%d').date()
        new_time = datetime.strptime(new_time, '%H:%M').time()
    except ValueError:
        return Response({'error': 'Invalid date or time format'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if new slot is available
    is_booked = Appointment.objects.filter(
        staff=appointment.staff,
        date=new_date,
        start_time=new_time,
        status__in=['pending', 'confirmed']
    ).exclude(id=appointment_id).exists()
    
    if is_booked:
        return Response({'error': 'Selected time slot is not available'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update appointment
    old_date = appointment.date
    old_time = appointment.start_time
    
    appointment.date = new_date
    appointment.start_time = new_time
    duration = timedelta(minutes=appointment.appointment_type.duration_minutes)
    end_datetime = datetime.combine(new_date, new_time) + duration
    appointment.end_time = end_datetime.time()
    appointment.save()
    
    # Add note about rescheduling
    note = f"Rescheduled from {old_date} {old_time} to {new_date} {new_time}"
    if appointment.notes:
        appointment.notes += f"\n{note}"
    else:
        appointment.notes = note
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentFeedbackCreateAPIView(generics.CreateAPIView):
    """Create feedback for a completed appointment"""
    serializer_class = AppointmentFeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class MyFeedbackListAPIView(generics.ListAPIView):
    """List user's appointment feedback"""
    serializer_class = AppointmentFeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AppointmentFeedback.objects.filter(
            appointment__client=self.request.user
        ).order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_statistics(request):
    """Get user's appointment statistics"""
    user = request.user
    
    stats = {
        'total_appointments': Appointment.objects.filter(client=user).count(),
        'completed_appointments': Appointment.objects.filter(
            client=user, status='completed'
        ).count(),
        'upcoming_appointments': Appointment.objects.filter(
            client=user, status__in=['pending', 'confirmed'],
            date__gte=timezone.now().date()
        ).count(),
        'cancelled_appointments': Appointment.objects.filter(
            client=user, status='cancelled'
        ).count(),
        'no_show_appointments': Appointment.objects.filter(
            client=user, status='no_show'
        ).count(),
        'average_rating': AppointmentFeedback.objects.filter(
            appointment__client=user
        ).aggregate(avg=Avg('overall_rating'))['avg'] or 0
    }
    
    return Response(stats)


# Admin views for staff
class StaffAppointmentListAPIView(generics.ListAPIView):
    """List appointments for staff members"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Check if user is staff
        if not hasattr(self.request.user, 'staff_profile'):
            return Appointment.objects.none()
        
        staff = self.request.user.staff_profile
        queryset = Appointment.objects.filter(staff=staff)
        
        # Filter by date
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset.order_by('date', 'start_time')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_appointment(request, appointment_id):
    """Confirm an appointment (staff only)"""
    if not hasattr(request.user, 'staff_profile'):
        return Response({'error': 'Only staff can confirm appointments'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if appointment.status != 'pending':
        return Response({'error': 'Only pending appointments can be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Assign room if provided
    room_id = request.data.get('room_id')
    if room_id:
        try:
            room = AppointmentRoom.objects.get(id=room_id, is_available=True)
            appointment.room = room
        except AppointmentRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    appointment.confirm(request.user)
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_appointment(request, appointment_id):
    """Mark appointment as completed (staff only)"""
    if not hasattr(request.user, 'staff_profile'):
        return Response({'error': 'Only staff can complete appointments'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if appointment.status != 'confirmed':
        return Response({'error': 'Only confirmed appointments can be completed'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update arrival and departure times if provided
    arrival_time = request.data.get('arrival_time')
    departure_time = request.data.get('departure_time')
    
    if arrival_time:
        appointment.arrival_time = arrival_time
    if departure_time:
        appointment.departure_time = departure_time
    
    appointment.complete()
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)