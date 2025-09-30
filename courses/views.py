from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from .models import Course, CourseCategory, Enrollment


class CourseListView(ListView):
    """List view for courses"""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published').select_related('category', 'instructor')
        
        # Filter by category if specified
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CourseCategory.objects.filter(is_active=True)
        context['featured_courses'] = Course.objects.filter(
            status='published'
        ).select_related('category', 'instructor')[:6]
        context['total_courses'] = Course.objects.filter(status='published').count()
        context['free_courses_count'] = Course.objects.filter(
            status='published', is_free=True
        ).count()
        context['popular_courses'] = Course.objects.filter(
            status='published'
        ).select_related('category', 'instructor')[:5]
        return context


class CourseCategoryView(ListView):
    """List view for courses in a specific category"""
    model = Course
    template_name = 'courses/course_category.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(CourseCategory, slug=self.kwargs['slug'])
        return Course.objects.filter(
            status='published',
            category=self.category
        ).select_related('category', 'instructor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CourseDetailView(DetailView):
    """Detail view for individual courses"""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    
    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('category', 'instructor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Get related courses
        context['related_courses'] = Course.objects.filter(
            status='published',
            category=course.category
        ).exclude(id=course.id).select_related('category', 'instructor')[:3]
        
        # Get user's enrollment status
        if self.request.user.is_authenticated:
            try:
                context['user_enrollment'] = Enrollment.objects.get(
                    user=self.request.user,
                    course=course
                )
            except Enrollment.DoesNotExist:
                context['user_enrollment'] = None
        else:
            context['user_enrollment'] = None
            
        return context


class CoursePurchaseView(CreateView):
    """View for purchasing courses"""
    template_name = 'courses/course_purchase.html'
    
    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=kwargs['slug'])
        return render(request, self.template_name, {'course': course})


class CourseEnrollView(CreateView):
    """View for enrolling in courses"""
    model = Enrollment
    fields = []
    template_name = 'courses/course_enroll.html'
    
    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        form.instance.user = self.request.user
        form.instance.course = course
        response = super().form_valid(form)
        return response


class CourseLearningView(DetailView):
    """View for course learning interface"""
    model = Course
    template_name = 'courses/course_learning.html'
    context_object_name = 'course'
    slug_field = 'slug'


class CourseModuleView(DetailView):
    """View for course modules"""
    model = Course
    template_name = 'courses/course_module.html'
    context_object_name = 'course'
    slug_field = 'slug'


class CourseLessonView(DetailView):
    """View for course lessons"""
    model = Course
    template_name = 'courses/course_lesson.html'
    context_object_name = 'course'
    slug_field = 'slug'


class CourseProgressView(DetailView):
    """View for course progress"""
    model = Course
    template_name = 'courses/course_progress.html'
    context_object_name = 'course'
    slug_field = 'slug'


class LessonCompleteView(CreateView):
    """View for completing lessons"""
    template_name = 'courses/lesson_complete.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CourseReviewView(CreateView):
    """View for course reviews"""
    template_name = 'courses/course_review.html'
    
    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=kwargs['slug'])
        return render(request, self.template_name, {'course': course})


class UserCoursesView(ListView):
    """View for user's enrolled courses"""
    model = Enrollment
    template_name = 'courses/user_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 10
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course')


class FreeCourseListView(ListView):
    """List view for free courses"""
    model = Course
    template_name = 'courses/free_course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        return Course.objects.filter(
            status='published',
            is_free=True
        ).select_related('category', 'instructor')