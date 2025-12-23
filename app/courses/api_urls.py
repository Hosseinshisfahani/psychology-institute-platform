from django.urls import path
from .api_views import (
    CourseLearnAPIView, 
    mark_lesson_complete, 
    update_watch_time,
    enroll_course,
    UserCoursesAPIView,
    add_to_cart,
    validate_coupon,
    user_purchases,
    purchase_course,
    CourseListAPIView,
    CourseCategoryListAPIView,
    CourseDetailAPIView,
    toggle_course_like,
    CourseCommentListCreateView
)

urlpatterns = [
    # Course listing and categories
    path('', CourseListAPIView.as_view(), name='api_course_list'),
    path('categories/', CourseCategoryListAPIView.as_view(), name='api_course_categories'),
    path('<slug:slug>/', CourseDetailAPIView.as_view(), name='api_course_detail'),
    
    # Course learning
    path('learn/<slug:slug>/', CourseLearnAPIView.as_view(), name='api_course_learn'),
    path('lesson/<int:lesson_id>/complete/', mark_lesson_complete, name='api_mark_lesson_complete'),
    path('lesson/<int:lesson_id>/watch-time/', update_watch_time, name='api_update_watch_time'),
    path('enroll/<slug:course_slug>/', enroll_course, name='api_enroll_course'),
    path('my-courses/', UserCoursesAPIView.as_view(), name='api_user_courses'),
    
    # Purchase and cart
    path('add-to-cart/<slug:course_slug>/', add_to_cart, name='api_add_to_cart'),
    path('purchase/<slug:course_slug>/', purchase_course, name='api_purchase_course'),
    path('validate-coupon/', validate_coupon, name='api_validate_coupon'),
    path('my-purchases/', user_purchases, name='api_user_purchases'),
    
    # Likes and Comments
    path('<slug:course_slug>/like/', toggle_course_like, name='api_toggle_like'),
    path('<slug:course_slug>/comments/', CourseCommentListCreateView.as_view(), name='api_comment_list_create'),
]
