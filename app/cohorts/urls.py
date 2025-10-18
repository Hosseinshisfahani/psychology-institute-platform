from django.urls import path
from . import views

app_name = 'cohorts'

urlpatterns = [
    # Cohorts
    path('', views.CohortListView.as_view(), name='cohort_list'),
    path('<int:pk>/', views.CohortDetailView.as_view(), name='cohort_detail'),
    path('<int:cohort_id>/enroll/', views.CohortEnrollView.as_view(), name='cohort_enroll'),
    
    # User cohorts
    path('my-cohorts/', views.UserCohortsView.as_view(), name='user_cohorts'),
]
