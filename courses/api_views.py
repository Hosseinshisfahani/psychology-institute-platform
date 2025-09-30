from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Course, Lesson, Enrollment, LessonProgress
from .serializers import CourseDetailSerializer, LessonProgressSerializer, EnrollmentSerializer
from django.db import transaction

class CourseLearnAPIView(generics.RetrieveAPIView):
    """
    API view for course learning interface
    """
    queryset = Course.objects.filter(status='published')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_object(self):
        course = super().get_object()
        # Check if user is enrolled
        if not Enrollment.objects.filter(user=self.request.user, course=course).exists():
            raise PermissionError("شما در این دوره ثبت‌نام نکرده‌اید")
        return course

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_lesson_complete(request, lesson_id):
    """
    Mark a lesson as completed
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(user=request.user, course=lesson.course).exists():
        return Response(
            {'error': 'شما در این دوره ثبت‌نام نکرده‌اید'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    with transaction.atomic():
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'is_completed': True}
        )
        
        if not created and not progress.is_completed:
            progress.is_completed = True
            progress.save()
        
        # Check if all lessons are completed to mark course as completed
        total_lessons = lesson.course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__course=lesson.course,
            is_completed=True
        ).count()
        
        if total_lessons == completed_lessons:
            enrollment = Enrollment.objects.get(user=request.user, course=lesson.course)
            enrollment.is_completed = True
            enrollment.save()
    
    serializer = LessonProgressSerializer(progress)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_watch_time(request, lesson_id):
    """
    Update lesson watch time
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    watch_time = request.data.get('watch_time', 0)
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(user=request.user, course=lesson.course).exists():
        return Response(
            {'error': 'شما در این دوره ثبت‌نام نکرده‌اید'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'watch_time': watch_time}
    )
    
    if not created:
        progress.watch_time = max(progress.watch_time, watch_time)
        progress.save()
    
    serializer = LessonProgressSerializer(progress)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_course(request, course_slug):
    """
    Enroll user in a course
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        message = 'با موفقیت در دوره ثبت‌نام شدید'
        status_code = status.HTTP_201_CREATED
    else:
        message = 'شما قبلاً در این دوره ثبت‌نام کرده‌اید'
        status_code = status.HTTP_200_OK
    
    serializer = EnrollmentSerializer(enrollment)
    return Response({
        'message': message,
        'enrollment': serializer.data
    }, status=status_code)

class UserCoursesAPIView(generics.ListAPIView):
    """
    List user's enrolled courses
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related('course')
