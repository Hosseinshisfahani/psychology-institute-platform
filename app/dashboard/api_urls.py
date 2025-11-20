from django.urls import path
from . import api_views

app_name = 'dashboard_api'

urlpatterns = [
    # Authentication
    path('login/', api_views.LoginAPIView.as_view(), name='login'),
    path('signup/', api_views.SignupAPIView.as_view(), name='signup'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    path('auth-check/', api_views.AuthCheckAPIView.as_view(), name='auth_check'),
    
    # OTP Verification
    path('otp/send/', api_views.SendOTPAPIView.as_view(), name='send_otp'),
    path('otp/verify/', api_views.VerifyOTPAPIView.as_view(), name='verify_otp'),
    path('otp/config-check/', api_views.sms_config_check, name='sms_config_check'),
    
    # Profile
    path('profile/', api_views.ProfileAPIView.as_view(), name='profile'),
    
    # Stats
    path('stats/', api_views.stats_api, name='stats'),
    
    # Financial Report
    path('financial-report/', api_views.financial_report_api, name='financial_report'),
]
