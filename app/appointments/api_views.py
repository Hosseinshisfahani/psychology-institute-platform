from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import datetime, timedelta

from .models import (
    Staff, Room, AppointmentType, TimeSlot, Appointment,
    AppointmentCancellation, AppointmentReminder, AppointmentFeedback
)
from .serializers import (
    StaffSerializer, RoomSerializer, AppointmentTypeSerializer,
    TimeSlotSerializer, AppointmentSerializer, AppointmentCreateSerializer,
    AppointmentCancellationSerializer, AppointmentReminderSerializer,
    AppointmentFeedbackSerializer, AdminAppointmentSerializer, AdminStaffSerializer
)


# Public API Views (for users)
class AppointmentTypeListAPIView(generics.ListAPIView):
    """List all active appointment types"""
    serializer_class = AppointmentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AppointmentType.objects.filter(is_active=True)


class StaffListAPIView(generics.ListAPIView):
    """List available staff members"""
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Staff.objects.filter(
            is_available=True,
            can_accept_appointments=True
        ).select_related('user')


class RoomListAPIView(generics.ListAPIView):
    """List available rooms"""
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Room.objects.filter(is_available=True)


class TimeSlotListAPIView(generics.ListAPIView):
    """List available time slots"""
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['staff', 'day_of_week']
    
    def get_queryset(self):
        return TimeSlot.objects.filter(is_available=True).select_related('staff__user')


class MyAppointmentListAPIView(generics.ListAPIView):
    """List user's appointments"""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['-appointment_date', '-appointment_time']
    
    def get_queryset(self):
        return Appointment.objects.filter(
            user=self.request.user
        ).select_related(
            'appointment_type', 'staff__user', 'room'
        )


class MyAppointmentDetailAPIView(generics.RetrieveAPIView):
    """Get user's appointment details"""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Appointment.objects.filter(
            user=self.request.user
        ).select_related(
            'appointment_type', 'staff__user', 'room'
        )


class CreateAppointmentAPIView(generics.CreateAPIView):
    """Create a new appointment request"""
    serializer_class = AppointmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        user=request.user
    )
    
    if appointment.status in ['completed', 'cancelled']:
        return Response(
            {'error': 'این قرار ملاقات قبلاً انجام یا لغو شده است.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reason = request.data.get('reason', '')
    appointment.cancel(cancelled_by=request.user, reason=reason)
    
    return Response({
        'message': 'قرار ملاقات با موفقیت لغو شد.'
    })


class AppointmentFeedbackCreateAPIView(generics.CreateAPIView):
    """Submit feedback for a completed appointment"""
    serializer_class = AppointmentFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        appointment = serializer.validated_data['appointment']
        
        # Verify appointment belongs to user and is completed
        if appointment.user != self.request.user:
            raise serializers.ValidationError('شما نمی‌توانید برای این قرار ملاقات بازخورد ثبت کنید.')
        
        if appointment.status != 'completed':
            raise serializers.ValidationError('فقط برای قرارهای ملاقات انجام شده می‌توان بازخورد ثبت کرد.')
        
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_available_slots(request):
    """Get available appointment slots for a specific date"""
    date_str = request.query_params.get('date')
    staff_id = request.query_params.get('staff')
    appointment_type_id = request.query_params.get('appointment_type')
    
    if not date_str:
        return Response(
            {'error': 'تاریخ الزامی است.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'فرمت تاریخ نامعتبر است. از فرمت YYYY-MM-DD استفاده کنید.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get day of week
    day_of_week = appointment_date.weekday()
    
    # Get time slots for this day
    time_slots = TimeSlot.objects.filter(
        day_of_week=day_of_week,
        is_available=True
    )
    
    if staff_id:
        time_slots = time_slots.filter(staff_id=staff_id)
    
    # Get appointment type duration
    duration_minutes = 60  # default
    if appointment_type_id:
        try:
            appointment_type = AppointmentType.objects.get(id=appointment_type_id)
            duration_minutes = appointment_type.duration_minutes
        except AppointmentType.DoesNotExist:
            pass
    
    # Get existing appointments for this date
    existing_appointments = Appointment.objects.filter(
        appointment_date=appointment_date,
        status__in=['pending', 'confirmed']
    )
    if staff_id:
        existing_appointments = existing_appointments.filter(staff_id=staff_id)
    
    # Calculate available slots
    available_slots = []
    
    for time_slot in time_slots:
        # Generate slots within the time slot
        current_time = datetime.combine(appointment_date, time_slot.start_time)
        end_time = datetime.combine(appointment_date, time_slot.end_time)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            slot_time = current_time.time()
            
            # Check if this slot is available
            conflicts = existing_appointments.filter(
                appointment_time=slot_time
            )
            
            if time_slot.staff:
                conflicts = conflicts.filter(staff=time_slot.staff)
            
            if conflicts.count() < time_slot.max_appointments:
                available_slots.append({
                    'time': slot_time.strftime('%H:%M'),
                    'staff': StaffSerializer(time_slot.staff).data if time_slot.staff else None,
                    'available_count': time_slot.max_appointments - conflicts.count()
                })
            
            current_time += timedelta(minutes=30)  # 30-minute intervals
    
    return Response({
        'date': date_str,
        'available_slots': available_slots
    })


# Admin API Views
class AdminAppointmentListAPIView(generics.ListAPIView):
    """List all appointments for admin"""
    serializer_class = AdminAppointmentSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'staff', 'room']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'purpose']
    ordering_fields = ['appointment_date', 'appointment_time', 'created_at']
    ordering = ['-appointment_date', '-appointment_time']
    
    def get_queryset(self):
        return Appointment.objects.all().select_related(
            'user', 'appointment_type', 'staff__user', 'room', 'confirmed_by'
        )


class AdminAppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete an appointment for admin"""
    serializer_class = AdminAppointmentSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Appointment.objects.all().select_related(
            'user', 'appointment_type', 'staff__user', 'room', 'confirmed_by'
        )


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def confirm_appointment(request, appointment_id):
    """Confirm an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'pending':
        return Response(
            {'error': 'این قرار ملاقات قبلاً تأیید یا لغو شده است.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    notes = request.data.get('notes', '')
    staff_id = request.data.get('staff_id')
    room_id = request.data.get('room_id')
    
    staff = None
    room = None
    
    if staff_id:
        staff = get_object_or_404(Staff, id=staff_id)
    
    if room_id:
        room = get_object_or_404(Room, id=room_id)
    
    appointment.confirm(
        confirmed_by=request.user,
        notes=notes,
        staff=staff,
        room=room
    )
    
    serializer = AdminAppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def reject_appointment(request, appointment_id):
    """Reject an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'pending':
        return Response(
            {'error': 'این قرار ملاقات قبلاً تأیید یا لغو شده است.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reason = request.data.get('reason', '')
    appointment.cancel(cancelled_by=request.user, reason=reason)
    
    return Response({
        'message': 'قرار ملاقات رد شد.'
    })


class AdminStaffListAPIView(generics.ListCreateAPIView):
    """List and create staff for admin"""
    serializer_class = AdminStaffSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_available', 'can_accept_appointments']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'title']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Staff.objects.all().select_related('user')


class AdminStaffDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete staff for admin"""
    serializer_class = AdminStaffSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Staff.objects.all().select_related('user')


class AdminRoomListAPIView(generics.ListCreateAPIView):
    """List and create rooms for admin"""
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building', 'floor', 'is_available']
    search_fields = ['name', 'building', 'facilities']
    ordering_fields = ['name', 'building', 'floor']
    ordering = ['building', 'floor', 'name']
    
    def get_queryset(self):
        return Room.objects.all()


class AdminRoomDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete room for admin"""
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Room.objects.all()


class AdminAppointmentTypeListAPIView(generics.ListCreateAPIView):
    """List and create appointment types for admin"""
    serializer_class = AppointmentTypeSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'requires_approval']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'duration_minutes']
    ordering = ['name']
    
    def get_queryset(self):
        return AppointmentType.objects.all()


class AdminAppointmentTypeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete appointment type for admin"""
    serializer_class = AppointmentTypeSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return AppointmentType.objects.all()


class AdminTimeSlotListAPIView(generics.ListCreateAPIView):
    """List and create time slots for admin"""
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['staff', 'day_of_week', 'is_available']
    ordering_fields = ['day_of_week', 'start_time']
    ordering = ['day_of_week', 'start_time']
    
    def get_queryset(self):
        return TimeSlot.objects.all().select_related('staff__user')


class AdminTimeSlotDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete time slot for admin"""
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return TimeSlot.objects.all().select_related('staff__user')