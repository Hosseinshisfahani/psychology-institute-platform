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
    queryset = SessionType.objects.filter(is_available=True)
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
