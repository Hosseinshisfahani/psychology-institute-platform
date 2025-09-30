from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from .models import User, UserProfile, Notification
from .forms import CustomSignupForm, CustomLoginForm, ProfileEditForm
from courses.models import Enrollment
from tests.models import TestResult
from therapy_sessions.models import Session


class DashboardView(LoginRequiredMixin, ListView):
    """Main dashboard view"""
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'notifications'
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        )[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user statistics
        context['enrolled_courses_count'] = Enrollment.objects.filter(user=user).count()
        context['completed_tests_count'] = TestResult.objects.filter(session__user=user).count()
        context['upcoming_sessions_count'] = Session.objects.filter(
            client=user, 
            status='scheduled',
            scheduled_date__gte=timezone.now().date()
        ).count()
        context['certificates_count'] = 0  # Placeholder for certificates
        context['sessions_count'] = Session.objects.filter(client=user).count()
        
        # Get recent activities (placeholder)
        context['recent_activities'] = []
        
        # Get current date
        context['current_date'] = timezone.now()
        
        # Get unread notifications count
        context['unread_notifications_count'] = Notification.objects.filter(
            user=user, 
            is_read=False
        ).count()
        
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = User
    template_name = 'dashboard/profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user statistics
        context['enrolled_courses_count'] = Enrollment.objects.filter(user=user).count()
        context['completed_tests_count'] = TestResult.objects.filter(session__user=user).count()
        context['sessions_count'] = Session.objects.filter(client=user).count()
        context['certificates_count'] = 0  # Placeholder for certificates
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """User profile edit view"""
    model = User
    template_name = 'dashboard/profile_edit.html'
    fields = ['first_name', 'last_name', 'phone_number', 'birth_date', 'gender', 'address', 'city', 'postal_code', 'bio', 'profile_image', 'license_number', 'specialization', 'experience_years', 'hourly_rate', 'is_available']
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        messages.success(self.request, 'پروفایل شما با موفقیت به‌روزرسانی شد.')
        return reverse('dashboard:profile')


class ChangePasswordView(LoginRequiredMixin, CreateView):
    """Change password view"""
    template_name = 'dashboard/change_password.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class NotificationListView(LoginRequiredMixin, ListView):
    """User notifications list"""
    model = Notification
    template_name = 'dashboard/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all notifications for filtering
        all_notifications = Notification.objects.filter(user=user).order_by('-created_at')
        context['unread_notifications'] = all_notifications.filter(is_read=False)
        context['read_notifications'] = all_notifications.filter(is_read=True)
        
        return context


class NotificationReadView(LoginRequiredMixin, CreateView):
    """Mark notification as read"""
    model = Notification
    fields = []
    
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=kwargs['pk'], user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})


class MarkAllNotificationsReadView(LoginRequiredMixin, CreateView):
    """Mark all notifications as read"""
    model = Notification
    fields = []
    
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})


class SettingsView(LoginRequiredMixin, CreateView):
    """User settings view"""
    template_name = 'dashboard/settings.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class PreferencesView(LoginRequiredMixin, CreateView):
    """User preferences view"""
    template_name = 'dashboard/preferences.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class UserStatsView(LoginRequiredMixin, CreateView):
    """User statistics view"""
    template_name = 'dashboard/user_stats.html'
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Calculate days since joined
        days_since_joined = (timezone.now().date() - user.date_joined.date()).days
        
        # Get user statistics
        enrolled_courses_count = Enrollment.objects.filter(user=user).count()
        completed_tests_count = TestResult.objects.filter(session__user=user).count()
        sessions_count = Session.objects.filter(client=user).count()
        
        # Get course progress
        course_progress = []
        enrollments = Enrollment.objects.filter(user=user).select_related('course')
        for enrollment in enrollments:
            total_lessons = enrollment.course.lessons.count()
            completed_lessons = enrollment.lesson_progress.filter(is_completed=True).count()
            progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            course_progress.append({
                'title': enrollment.course.title,
                'progress': round(progress, 1)
            })
        
        # Get recent test results
        recent_test_results = TestResult.objects.filter(session__user=user).select_related('session__test').order_by('-generated_at')[:5]
        
        # Calculate monthly stats (placeholder)
        study_time_this_month = 45  # hours
        tests_this_month = 8
        sessions_this_month = 4
        completed_courses_count = 2
        
        context = {
            'days_since_joined': days_since_joined,
            'enrolled_courses_count': enrolled_courses_count,
            'completed_tests_count': completed_tests_count,
            'sessions_count': sessions_count,
            'course_progress': course_progress,
            'recent_test_results': recent_test_results,
            'study_time_this_month': study_time_this_month,
            'tests_this_month': tests_this_month,
            'sessions_this_month': sessions_this_month,
            'completed_courses_count': completed_courses_count,
        }
        
        return render(request, self.template_name, context)


# Custom Authentication Views
class CustomLoginView(BaseLoginView):
    """Custom login view with our template"""
    template_name = 'account/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard')
    
    def form_valid(self, form):
        # Handle remember me functionality
        remember_me = self.request.POST.get('remember')
        if not remember_me:
            # Set session to expire when browser is closed
            self.request.session.set_expiry(0)
        else:
            # Set session to expire in 2 weeks
            self.request.session.set_expiry(1209600)  # 2 weeks in seconds
        
        messages.success(self.request, f'خوش آمدید {form.get_user().full_name}!')
        return super().form_valid(form)


class CustomSignupView(FormView):
    """Custom signup view"""
    template_name = 'account/signup.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('dashboard:dashboard')
    
    def form_valid(self, form):
        user = form.save()
        # Specify the backend for authentication
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, f'حساب کاربری شما با موفقیت ایجاد شد! خوش آمدید {user.full_name}')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'لطفاً خطاهای فرم را برطرف کنید.')
        return super().form_invalid(form)


class CustomLogoutView(BaseLogoutView):
    """Custom logout view"""
    next_page = reverse_lazy('blog:home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'با موفقیت از حساب کاربری خود خارج شدید.')
        return super().dispatch(request, *args, **kwargs)