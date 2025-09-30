"""
URL configuration for psychology_institute project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication (Custom views)
    path('accounts/', include('dashboard.auth_urls')),
    
    # API
    path('api/', include('rest_framework.urls')),
    path('api/blog/', include('blog.api_urls')),
    path('api/dashboard/', include('dashboard.api_urls')),
    path('api/courses/', include('courses.api_urls')),
    path('api/therapy/', include('therapy_sessions.api_urls')),
    path('api/admin/', include('admin_panel.api_urls')),
    
    # Apps
    path('', include('blog.urls')),
    path('tests/', include('tests.urls')),
    path('courses/', include('courses.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('sessions/', include('therapy_sessions.urls')),
    path('payment/', include('payment.urls')),
    path('reports/', include('reports.urls')),
    path('sales/', include('sales.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
