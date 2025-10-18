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
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token

# Health check view
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for Docker and load balancers"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'psychology-institute',
        'version': '1.0.0'
    })

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Admin
    path('admin/', admin.site.urls),

    # CSRF token endpoint for SPA frontends
    path('csrf/', lambda request: JsonResponse({'csrfToken': get_token(request)}), name='csrf_token'),
    
    # Authentication (Custom views)
    path('accounts/', include('app.dashboard.auth_urls')),
    
    # API
    path('api/', include('rest_framework.urls')),
    path('api/blog/', include('app.blog.api_urls')),
    path('api/dashboard/', include('app.dashboard.api_urls')),
    path('api/courses/', include('app.courses.api_urls')),
    path('api/therapy/', include('app.therapy_sessions.api_urls')),
    path('api/admin/', include('app.admin_panel.api_urls')),
    path('api/workshops/', include('app.workshops.api_urls')),
    path('api/packages/', include('app.packages.api_urls')),
    
    # Apps
    path('', include('app.blog.urls')),
    path('tests/', include('app.tests.urls')),
    path('courses/', include('app.courses.urls')),
    path('dashboard/', include('app.dashboard.urls')),
    path('sessions/', include('app.therapy_sessions.urls')),
    path('payment/', include('app.payment.urls')),
    path('reports/', include('app.reports.urls')),
    path('sales/', include('app.sales.urls')),
    path('admin-panel/', include('app.admin_panel.urls')),
    path('workshops/', include('app.workshops.urls')),
    path('packages/', include('app.packages.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
