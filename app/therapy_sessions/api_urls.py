from django.urls import path
from .api_views import (
    TherapistListAPIView, TherapistDetailAPIView, SessionTypeListAPIView,
    SessionBookingCreateAPIView, UserSessionListAPIView, SessionDetailAPIView,
    SessionRatingAPIView, therapist_availability, confirm_session,
    cancel_session, TherapistStatsAPIView, create_session_booking,
    user_bookings, confirm_booking, reject_booking, therapist_bookings
)

urlpatterns = [
    # Therapists
    path('therapists/', TherapistListAPIView.as_view(), name='api_therapist_list'),
    path('therapists/<int:pk>/', TherapistDetailAPIView.as_view(), name='api_therapist_detail'),
    path('therapists/<int:therapist_id>/availability/', therapist_availability, name='api_therapist_availability'),
    path('therapists/<int:therapist_id>/stats/', TherapistStatsAPIView.as_view(), name='api_therapist_stats'),
    
    # Session Types
    path('session-types/', SessionTypeListAPIView.as_view(), name='api_session_types'),
    
    # New booking flow (therapist confirmation required)
    path('bookings/create/', create_session_booking, name='api_create_session_booking'),
    path('bookings/my-bookings/', user_bookings, name='api_user_bookings'),
    path('bookings/<int:booking_id>/confirm/', confirm_booking, name='api_confirm_booking'),
    path('bookings/<int:booking_id>/reject/', reject_booking, name='api_reject_booking'),
    path('therapist/bookings/', therapist_bookings, name='api_therapist_bookings'),
    
    # Legacy bookings (for backward compatibility)
    path('bookings/', SessionBookingCreateAPIView.as_view(), name='api_session_booking'),
    path('bookings/<int:booking_id>/confirm-legacy/', confirm_session, name='api_confirm_session'),
    
    # Sessions
    path('sessions/', UserSessionListAPIView.as_view(), name='api_user_sessions'),
    path('sessions/<int:pk>/', SessionDetailAPIView.as_view(), name='api_session_detail'),
    path('sessions/<int:session_id>/rate/', SessionRatingAPIView.as_view(), name='api_session_rating'),
    path('sessions/<int:session_id>/cancel/', cancel_session, name='api_cancel_session'),
]
