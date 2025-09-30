from django.urls import path
from . import views

app_name = 'therapy_sessions'

urlpatterns = [
    # Session booking
    path('', views.SessionListView.as_view(), name='session_list'),
    path('book/', views.SessionBookingView.as_view(), name='session_booking'),
    path('therapists/', views.TherapistListView.as_view(), name='therapist_list'),
    path('therapist/<int:pk>/', views.TherapistDetailView.as_view(), name='therapist_detail'),
    path('therapist/<int:pk>/availability/', views.TherapistAvailabilityView.as_view(), name='therapist_availability'),
    
    # Session management
    path('my-sessions/', views.UserSessionsView.as_view(), name='user_sessions'),
    path('session/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('session/<int:pk>/cancel/', views.SessionCancelView.as_view(), name='session_cancel'),
    path('session/<int:pk>/reschedule/', views.SessionRescheduleView.as_view(), name='session_reschedule'),
    
    # Session types
    path('types/', views.SessionTypeListView.as_view(), name='session_type_list'),
    
    # Session notes (for therapists)
    path('session/<int:pk>/notes/', views.SessionNotesView.as_view(), name='session_notes'),
    path('session/<int:pk>/notes/add/', views.SessionNoteCreateView.as_view(), name='session_note_create'),
    
    # Session rating
    path('session/<int:pk>/rate/', views.SessionRatingView.as_view(), name='session_rating'),
    
    # Therapist dashboard
    path('therapist/dashboard/', views.TherapistDashboardView.as_view(), name='therapist_dashboard'),
    path('therapist/sessions/', views.TherapistSessionsView.as_view(), name='therapist_sessions'),
    path('therapist/availability/', views.TherapistAvailabilityManageView.as_view(), name='therapist_availability_manage'),
]
