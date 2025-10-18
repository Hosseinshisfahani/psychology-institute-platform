from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Reports dashboard
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),
    
    # Financial reports
    path('financial/', views.FinancialReportsView.as_view(), name='financial_reports'),
    path('financial/revenue/', views.RevenueReportView.as_view(), name='revenue_report'),
    path('financial/expenses/', views.ExpensesReportView.as_view(), name='expenses_report'),
    path('financial/profit-loss/', views.ProfitLossReportView.as_view(), name='profit_loss_report'),
    
    # Analytics reports
    path('analytics/', views.AnalyticsReportsView.as_view(), name='analytics_reports'),
    path('analytics/users/', views.UserAnalyticsView.as_view(), name='user_analytics'),
    path('analytics/courses/', views.CourseAnalyticsView.as_view(), name='course_analytics'),
    path('analytics/tests/', views.TestAnalyticsView.as_view(), name='test_analytics'),
    path('analytics/sessions/', views.SessionAnalyticsView.as_view(), name='session_analytics'),
    
    # Export reports
    path('export/<int:report_id>/', views.ExportReportView.as_view(), name='export_report'),
    path('export/financial/<str:format>/', views.ExportFinancialReportView.as_view(), name='export_financial_report'),
    
    # Custom reports
    path('custom/', views.CustomReportView.as_view(), name='custom_report'),
    path('custom/create/', views.CreateCustomReportView.as_view(), name='create_custom_report'),
]

