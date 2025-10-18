from django.urls import path
from .api_views import (
    CohortListView, CohortDetailView, enroll_cohort,
    user_cohorts, cohort_sessions, cohort_installments,
    mark_attendance
)

urlpatterns = [
    # Cohorts
    path('', CohortListView.as_view(), name='api_cohort_list'),
    path('<int:cohort_id>/', CohortDetailView.as_view(), name='api_cohort_detail'),
    path('<int:cohort_id>/enroll/', enroll_cohort, name='api_cohort_enroll'),
    
    # User cohorts
    path('my-cohorts/', user_cohorts, name='api_user_cohorts'),
    path('<int:cohort_id>/sessions/', cohort_sessions, name='api_cohort_sessions'),
    
    # Installments
    path('enrollments/<int:enrollment_id>/installments/', cohort_installments, name='api_cohort_installments'),
    
    # Attendance (for instructors)
    path('sessions/<int:session_id>/attendance/', mark_attendance, name='api_mark_attendance'),
]
