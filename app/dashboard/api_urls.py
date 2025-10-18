from django.urls import path
from . import api_views

app_name = 'dashboard_api'

urlpatterns = [
    # Authentication
    path('login/', api_views.LoginAPIView.as_view(), name='login'),
    path('signup/', api_views.SignupAPIView.as_view(), name='signup'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    
    # Profile
    path('profile/', api_views.ProfileAPIView.as_view(), name='profile'),
    
    # Financial Report
    path('financial-report/', api_views.financial_report_api, name='financial_report'),
]
