from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course list and categories
    path('', views.CourseListView.as_view(), name='course_list'),
    path('category/<slug:slug>/', views.CourseCategoryView.as_view(), name='course_category'),
    
    # Course details and purchase
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<slug:slug>/purchase/', views.CoursePurchaseView.as_view(), name='course_purchase'),
    path('course/<slug:slug>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
    
    # Course learning
    path('learn/<slug:slug>/', views.CourseLearningView.as_view(), name='course_learning'),
    path('learn/<slug:slug>/module/<int:module_pk>/', views.CourseModuleView.as_view(), name='course_module'),
    path('learn/<slug:slug>/lesson/<int:lesson_pk>/', views.CourseLessonView.as_view(), name='course_lesson'),
    
    # Progress tracking
    path('progress/<slug:slug>/', views.CourseProgressView.as_view(), name='course_progress'),
    path('lesson/<int:lesson_pk>/complete/', views.LessonCompleteView.as_view(), name='lesson_complete'),
    
    # Reviews
    path('course/<slug:slug>/review/', views.CourseReviewView.as_view(), name='course_review'),
    
    # My courses
    path('my-courses/', views.UserCoursesView.as_view(), name='user_courses'),
    
    # Free courses
    path('free/', views.FreeCourseListView.as_view(), name='free_course_list'),
]

