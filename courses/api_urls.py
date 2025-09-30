from django.urls import path
from .api_views import (
    CourseLearnAPIView, 
    mark_lesson_complete, 
    update_watch_time,
    enroll_course,
    UserCoursesAPIView
)

urlpatterns = [
    path('learn/<slug:slug>/', CourseLearnAPIView.as_view(), name='api_course_learn'),
    path('lesson/<int:lesson_id>/complete/', mark_lesson_complete, name='api_mark_lesson_complete'),
    path('lesson/<int:lesson_id>/watch-time/', update_watch_time, name='api_update_watch_time'),
    path('enroll/<slug:course_slug>/', enroll_course, name='api_enroll_course'),
    path('my-courses/', UserCoursesAPIView.as_view(), name='api_user_courses'),
]
