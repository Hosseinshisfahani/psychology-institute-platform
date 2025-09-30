from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import AdminNotification
from blog.models import Post, Comment
from tests.models import PsychologicalTest, TestSession
from courses.models import Course, Enrollment
from therapy_sessions.models import Session
from payment.models import Order
from dashboard.models import User


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only admin users can access"""
    
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or 
            self.request.user.is_superuser or
            self.request.user.user_type == 'admin'
        )


class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Main admin dashboard view"""
    template_name = 'admin_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User Statistics
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['clients'] = User.objects.filter(user_type='client').count()
        context['therapists'] = User.objects.filter(user_type='therapist').count()
        
        # Blog Statistics
        context['total_posts'] = Post.objects.count()
        context['published_posts'] = Post.objects.filter(status='published').count()
        context['total_comments'] = Comment.objects.count()
        
        # Test Statistics
        context['total_tests'] = PsychologicalTest.objects.count()
        context['total_test_sessions'] = TestSession.objects.count()
        
        # Course Statistics
        context['total_courses'] = Course.objects.count()
        context['total_enrollments'] = Enrollment.objects.count()
        
        # Session Statistics
        context['total_sessions'] = Session.objects.count()
        context['completed_sessions'] = Session.objects.filter(status='completed').count()
        
        # Financial Statistics
        context['total_orders'] = Order.objects.count()
        context['paid_orders'] = Order.objects.filter(status='paid').count()
        total_revenue = Order.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        context['total_revenue'] = float(total_revenue)
        
        # Recent Activity
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        context['recent_orders'] = Order.objects.order_by('-created_at')[:5]
        
        return context


class AdminUsersView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin users management view"""
    model = User
    template_name = 'admin_panel/users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        # Filter by user type
        user_type = self.request.GET.get('type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['clients'] = User.objects.filter(user_type='client').count()
        context['therapists'] = User.objects.filter(user_type='therapist').count()
        context['admins'] = User.objects.filter(user_type='admin').count()
        
        return context


class AdminOrdersView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin orders management view"""
    model = Order
    template_name = 'admin_panel/orders.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Order.objects.all().order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['paid_orders'] = Order.objects.filter(status='paid').count()
        total_revenue = Order.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        context['total_revenue'] = float(total_revenue)
        
        return context


class AdminReportsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin reports and analytics view"""
    template_name = 'admin_panel/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Top courses
        top_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:10]
        
        context['top_courses'] = top_courses
        
        return context


class AdminSettingsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Admin settings view"""
    template_name = 'admin_panel/settings.html'


class AdminLogsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin activity logs view"""
    model = AdminNotification
    template_name = 'admin_panel/logs.html'
    context_object_name = 'logs'
    paginate_by = 50


class AdminNotificationsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Admin notifications view"""
    model = AdminNotification
    template_name = 'admin_panel/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AdminNotification.objects.filter(
            Q(is_global=True) | Q(target_users=self.request.user)
        ).order_by('-created_at')
        
        return queryset