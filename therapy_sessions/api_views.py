from rest_framework import generics, views, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.utils import timezone
from .models import Therapist, Session, SessionType, SessionBooking
from .serializers import (
    TherapistSerializer, SessionTypeSerializer, SessionBookingSerializer,
    SessionSerializer, SessionRatingSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
import jdatetime

class TherapistListAPIView(generics.ListAPIView):
    """
    List all available therapists with filtering
    """
    serializer_class = TherapistSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'bio', 'education']
    ordering_fields = ['hourly_rate', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Therapist.objects.filter(is_available=True).select_related('user')
        
        # Filter by experience years
        experience = self.request.query_params.get('experience')
        if experience:
            if experience == '0-2':
                queryset = queryset.filter(experience_start_date__gte=timezone.now().date().replace(year=timezone.now().year-2))
            elif experience == '3-5':
                queryset = queryset.filter(
                    experience_start_date__gte=timezone.now().date().replace(year=timezone.now().year-5),
                    experience_start_date__lt=timezone.now().date().replace(year=timezone.now().year-3)
                )
            elif experience == '6-10':
                queryset = queryset.filter(
                    experience_start_date__gte=timezone.now().date().replace(year=timezone.now().year-10),
                    experience_start_date__lt=timezone.now().date().replace(year=timezone.now().year-6)
                )
            elif experience == '10+':
                queryset = queryset.filter(experience_start_date__lt=timezone.now().date().replace(year=timezone.now().year-10))
        
        return queryset

class TherapistDetailAPIView(generics.RetrieveAPIView):
    """
    Get therapist details
    """
    queryset = Therapist.objects.filter(is_available=True)
    serializer_class = TherapistSerializer
    permission_classes = [permissions.AllowAny]

class SessionTypeListAPIView(generics.ListAPIView):
    """
    List all available session types
    """
    queryset = SessionType.objects.filter(is_active=True)
    serializer_class = SessionTypeSerializer
    permission_classes = [permissions.AllowAny]

class SessionBookingCreateAPIView(generics.CreateAPIView):
    """
    Create a new session booking
    """
    serializer_class = SessionBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserSessionListAPIView(generics.ListAPIView):
    """
    List user's sessions
    """
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'therapist']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user).select_related(
            'therapist__user', 'session_type'
        )

class SessionDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    Get or update session details
    """
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)

class SessionRatingAPIView(generics.UpdateAPIView):
    """
    Rate a completed session
    """
    serializer_class = SessionRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Session.objects.filter(
            user=self.request.user,
            status='completed',
            rating__isnull=True
        )

    def perform_update(self, serializer):
        serializer.save()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def therapist_availability(request, therapist_id):
    """
    Get therapist availability for a specific date
    """
    therapist = get_object_or_404(Therapist, id=therapist_id, is_available=True)
    date_str = request.query_params.get('date')
    
    if not date_str:
        return Response({'error': 'تاریخ الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Parse Persian date
        date_obj = jdatetime.datetime.strptime(date_str, '%Y/%m/%d').date()
    except ValueError:
        return Response({'error': 'فرمت تاریخ نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get booked sessions for the date
    booked_sessions = Session.objects.filter(
        therapist=therapist,
        start_time__date=date_obj,
        status__in=['scheduled', 'in_progress']
    ).values_list('start_time__hour', 'end_time__hour')
    
    # Generate available time slots (9 AM to 9 PM)
    available_slots = []
    for hour in range(9, 21):
        is_available = True
        for start_hour, end_hour in booked_sessions:
            if start_hour <= hour < end_hour:
                is_available = False
                break
        
        if is_available:
            available_slots.append({
                'hour': hour,
                'time_display': f"{hour:02d}:00"
            })
    
    return Response({
        'therapist_id': therapist_id,
        'date': date_str,
        'available_slots': available_slots
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_session(request, booking_id):
    """
    Confirm a session booking
    """
    booking = get_object_or_404(SessionBooking, id=booking_id, user=request.user)
    
    if booking.status != 'pending':
        return Response(
            {'error': 'این رزرو قبلاً تایید یا لغو شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create session from booking
    session = Session.objects.create(
        user=booking.user,
        therapist=booking.therapist,
        session_type=booking.session_type,
        start_time=booking.preferred_date.replace(hour=booking.preferred_time.hour),
        end_time=booking.preferred_date.replace(
            hour=booking.preferred_time.hour + booking.duration.hour
        ),
        status='scheduled',
        notes=booking.notes
    )
    
    # Update booking status
    booking.status = 'confirmed'
    booking.save()
    
    serializer = SessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_session(request, session_id):
    """
    Cancel a session
    """
    session = get_object_or_404(Session, id=session_id, user=request.user)
    
    if session.status not in ['scheduled', 'pending']:
        return Response(
            {'error': 'این جلسه قابل لغو نیست'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    session.status = 'cancelled'
    session.save()
    
    return Response({'message': 'جلسه با موفقیت لغو شد'})

class TherapistStatsAPIView(views.APIView):
    """
    Get therapist statistics
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, therapist_id):
        therapist = get_object_or_404(Therapist, id=therapist_id)
        
        # Get session statistics
        total_sessions = Session.objects.filter(therapist=therapist).count()
        completed_sessions = Session.objects.filter(
            therapist=therapist, 
            status='completed'
        ).count()
        
        # Calculate average rating
        avg_rating = Session.objects.filter(
            therapist=therapist,
            status='completed',
            rating__isnull=False
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Get recent reviews
        recent_sessions = Session.objects.filter(
            therapist=therapist,
            status='completed',
            feedback__isnull=False
        ).order_by('-created_at')[:5]
        
        return Response({
            'therapist_id': therapist_id,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'average_rating': round(avg_rating, 1),
            'recent_reviews': SessionSerializer(recent_sessions, many=True).data
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_session_booking(request):
    """
    Create a new session booking request (therapist confirmation required)
    """
    therapist_id = request.data.get('therapist_id')
    session_type_id = request.data.get('session_type_id')
    preferred_date = request.data.get('preferred_date')
    preferred_time = request.data.get('preferred_time')
    mode = request.data.get('mode', 'online')
    goals = request.data.get('goals', '')
    notes = request.data.get('notes', '')
    location = request.data.get('location', '')
    
    if not all([therapist_id, session_type_id, preferred_date, preferred_time]):
        return Response(
            {'error': 'تمام فیلدهای الزامی باید پر شوند'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        therapist = get_object_or_404(User, id=therapist_id, user_type='therapist')
        session_type = get_object_or_404(SessionType, id=session_type_id, is_active=True)
    except:
        return Response(
            {'error': 'درمانگر یا نوع جلسه نامعتبر است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Parse date and time
    try:
        from datetime import datetime
        preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        preferred_time_obj = datetime.strptime(preferred_time, '%H:%M').time()
    except ValueError:
        return Response(
            {'error': 'فرمت تاریخ یا زمان نامعتبر است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create booking with expiration (24 hours)
    expires_at = timezone.now() + timezone.timedelta(hours=24)
    
    booking = SessionBooking.objects.create(
        user=request.user,
        therapist=therapist,
        session_type=session_type,
        preferred_date=preferred_date_obj,
        preferred_time=preferred_time_obj,
        mode=mode,
        goals=goals,
        notes=notes,
        location=location,
        price=session_type.price,
        expires_at=expires_at
    )
    
    # Send notification to therapist (in real app, use Celery task)
    # send_booking_notification.delay(booking.id)
    
    serializer = SessionBookingSerializer(booking)
    return Response({
        'message': 'درخواست رزرو جلسه ارسال شد. درمانگر ظرف 24 ساعت پاسخ خواهد داد.',
        'booking': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_bookings(request):
    """
    List user's session bookings
    """
    bookings = SessionBooking.objects.filter(user=request.user).select_related(
        'therapist', 'session_type'
    ).order_by('-created_at')
    
    data = []
    for booking in bookings:
        data.append({
            'id': booking.id,
            'therapist': {
                'id': booking.therapist.id,
                'name': booking.therapist.full_name,
                'specialization': getattr(booking.therapist, 'specialization', '')
            },
            'session_type': {
                'id': booking.session_type.id,
                'name': booking.session_type.name,
                'duration': booking.session_type.duration_minutes
            },
            'preferred_date': booking.preferred_date,
            'preferred_time': booking.preferred_time,
            'mode': booking.mode,
            'status': booking.status,
            'price': float(booking.price),
            'goals': booking.goals,
            'notes': booking.notes,
            'created_at': booking.created_at,
            'expires_at': booking.expires_at,
            'is_expired': booking.is_expired,
            'croom_class_url': booking.croom_class_url,
            'croom_meeting_id': booking.croom_meeting_id
        })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_booking(request, booking_id):
    """
    Confirm a booking (for therapists)
    """
    booking = get_object_or_404(SessionBooking, id=booking_id)
    
    # Check if user is the therapist
    if request.user != booking.therapist:
        return Response(
            {'error': 'فقط درمانگر مربوطه می‌تواند این رزرو را تایید کند'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if booking.status != 'pending':
        return Response(
            {'error': 'این رزرو قبلاً تایید یا رد شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    confirmed_date = request.data.get('confirmed_date')
    confirmed_time = request.data.get('confirmed_time')
    confirmation_notes = request.data.get('confirmation_notes', '')
    croom_class_url = request.data.get('croom_class_url', '')
    croom_meeting_id = request.data.get('croom_meeting_id', '')
    croom_password = request.data.get('croom_password', '')
    
    if not all([confirmed_date, confirmed_time]):
        return Response(
            {'error': 'تاریخ و زمان تایید الزامی است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from datetime import datetime
        confirmed_date_obj = datetime.strptime(confirmed_date, '%Y-%m-%d').date()
        confirmed_time_obj = datetime.strptime(confirmed_time, '%H:%M').time()
    except ValueError:
        return Response(
            {'error': 'فرمت تاریخ یا زمان نامعتبر است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update booking with croom details
    booking.croom_class_url = croom_class_url
    booking.croom_meeting_id = croom_meeting_id
    booking.croom_password = croom_password
    
    # Confirm booking and create session
    session = booking.confirm_booking(
        confirmed_date_obj,
        confirmed_time_obj,
        request.user,
        confirmation_notes
    )
    
    # Send confirmation notification to client (in real app, use Celery task)
    # send_booking_confirmation.delay(booking.id)
    
    return Response({
        'message': 'رزرو با موفقیت تایید شد',
        'session_id': session.id,
        'croom_class_url': croom_class_url,
        'croom_meeting_id': croom_meeting_id
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_booking(request, booking_id):
    """
    Reject a booking (for therapists)
    """
    booking = get_object_or_404(SessionBooking, id=booking_id)
    
    # Check if user is the therapist
    if request.user != booking.therapist:
        return Response(
            {'error': 'فقط درمانگر مربوطه می‌تواند این رزرو را رد کند'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if booking.status != 'pending':
        return Response(
            {'error': 'این رزرو قبلاً تایید یا رد شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rejection_reason = request.data.get('rejection_reason', '')
    
    booking.status = 'rejected'
    booking.confirmation_notes = rejection_reason
    booking.save()
    
    # Send rejection notification to client (in real app, use Celery task)
    # send_booking_rejection.delay(booking.id)
    
    return Response({
        'message': 'رزرو رد شد'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def therapist_bookings(request):
    """
    List booking requests for a therapist
    """
    bookings = SessionBooking.objects.filter(therapist=request.user).select_related(
        'user', 'session_type'
    ).order_by('-created_at')
    
    data = []
    for booking in bookings:
        data.append({
            'id': booking.id,
            'client': {
                'id': booking.user.id,
                'name': booking.user.full_name,
                'email': booking.user.email
            },
            'session_type': {
                'id': booking.session_type.id,
                'name': booking.session_type.name,
                'duration': booking.session_type.duration_minutes
            },
            'preferred_date': booking.preferred_date,
            'preferred_time': booking.preferred_time,
            'mode': booking.mode,
            'status': booking.status,
            'price': float(booking.price),
            'goals': booking.goals,
            'notes': booking.notes,
            'created_at': booking.created_at,
            'expires_at': booking.expires_at,
            'is_expired': booking.is_expired
        })
    
    return Response(data)
