from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from .models import Report, DashboardWidget, AnalyticsEvent


class ReportsDashboardView(ListView):
    """Reports dashboard view"""
    model = Report
    template_name = 'reports/dashboard.html'
    context_object_name = 'reports'
    paginate_by = 10


class FinancialReportsView(ListView):
    """Financial reports view"""
    model = Report
    template_name = 'reports/financial_reports.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def get_queryset(self):
        return Report.objects.filter(report_type='financial')


class RevenueReportView(DetailView):
    """Revenue report view"""
    model = Report
    template_name = 'reports/revenue_report.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(report_type='financial')


class ExpensesReportView(DetailView):
    """Expenses report view"""
    model = Report
    template_name = 'reports/expenses_report.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(report_type='financial')


class ProfitLossReportView(DetailView):
    """Profit and loss report view"""
    model = Report
    template_name = 'reports/profit_loss_report.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(report_type='financial')


class AnalyticsReportsView(ListView):
    """Analytics reports view"""
    model = Report
    template_name = 'reports/analytics_reports.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def get_queryset(self):
        return Report.objects.filter(report_type__in=['user_analytics', 'course_analytics', 'test_analytics', 'session_analytics'])


class UserAnalyticsView(DetailView):
    """User analytics view"""
    model = Report
    template_name = 'reports/user_analytics.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(report_type='user_analytics')


class CourseAnalyticsView(DetailView):
    """Course analytics view"""
    model = Report
    template_name = 'reports/course_analytics.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(report_type='course_analytics')


class TestAnalyticsView(DetailView):
    """Test analytics view"""
    model = Report
    template_name = 'reports/test_analytics.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(report_type='test_analytics')


class SessionAnalyticsView(DetailView):
    """Session analytics view"""
    model = Report
    template_name = 'reports/session_analytics.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(report_type='session_analytics')


class ExportReportView(DetailView):
    """Export report view"""
    model = Report
    template_name = 'reports/export_report.html'
    context_object_name = 'report'


class ExportFinancialReportView(CreateView):
    """Export financial report view"""
    template_name = 'reports/export_financial_report.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CustomReportView(CreateView):
    """Custom report view"""
    template_name = 'reports/custom_report.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CreateCustomReportView(CreateView):
    """Create custom report view"""
    model = Report
    fields = ['name', 'report_type', 'description', 'period_start', 'period_end']
    template_name = 'reports/create_custom_report.html'
    
    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        response = super().form_valid(form)
        return response