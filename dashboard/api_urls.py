from django.urls import path
from . import api_views

app_name = 'dashboard_api'

urlpatterns = [
    path('financial-report/', api_views.financial_report_api, name='financial_report'),
]
