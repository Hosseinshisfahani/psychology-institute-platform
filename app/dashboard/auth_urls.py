from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.CustomSignupView.as_view(), name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]
