
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import JsonResponse, FileResponse, StreamingHttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.utils.translation import gettext_lazy as _
import os
import re
import mimetypes

# Configure admin site
admin.site.site_header = "مدیریت موسسه روانشناسی"
admin.site.site_title = "پنل مدیریت موسسه روانشناسی"
admin.site.index_title = "به پنل مدیریت موسسه روانشناسی خوش آمدید"

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
    path('api/admin/', include('app.admin_panel.api_urls')),
    path('api/workshops/', include('app.workshops.api_urls')),
    path('api/packages/', include('app.packages.api_urls')),
    path('api/appointments/', include('app.appointments.api_urls')),
    path('api/payment/', include('app.payment.api_urls')),
    path('api/chat/', include('app.chat.api_urls')),
    
    # Redirect root to React frontend
    path('', RedirectView.as_view(url='http://localhost:3000', permanent=False), name='home_redirect'),
    
    # Apps (for API endpoints only)
    path('blog/', include('app.blog.urls')),
    path('tests/', include('app.tests.urls')),
    path('courses/', include('app.courses.urls')),
    path('dashboard/', include('app.dashboard.urls')),
    path('payment/', include('app.payment.urls')),
    path('reports/', include('app.reports.urls')),
    path('sales/', include('app.sales.urls')),
    path('admin-panel/', include('app.admin_panel.urls')),
    path('workshops/', include('app.workshops.urls')),
    path('packages/', include('app.packages.urls')),
    path('appointments/', include('app.appointments.urls')),
    path('chat/', include('app.chat.urls')),
]

# Serve media files in development
if settings.DEBUG:
    # Range-supporting media handler for seeking video/audio
    def media_serve(request, path):
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise Http404()

        file_size = os.path.getsize(full_path)
        content_type, _ = mimetypes.guess_type(full_path)
        content_type = content_type or 'application/octet-stream'

        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)

        def file_iterator(f, start=0, length=None, chunk_size=8192):
            f.seek(start)
            remaining = length
            while True:
                read_length = chunk_size if remaining is None else min(remaining, chunk_size)
                data = f.read(read_length)
                if not data:
                    break
                if remaining is not None:
                    remaining -= len(data)
                yield data

        if range_match:
            start = int(range_match.group(1))
            end_str = range_match.group(2)
            end = int(end_str) if end_str else file_size - 1
            if start >= file_size:
                # Invalid range
                response = StreamingHttpResponse(status=416)
                response['Content-Range'] = f'bytes */{file_size}'
                return response

            length = end - start + 1
            f = open(full_path, 'rb')
            response = StreamingHttpResponse(
                file_iterator(f, start=start, length=length),
                status=206,
                content_type=content_type,
            )
            response['Content-Length'] = str(length)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            return response

        # Fallback: full file
        f = open(full_path, 'rb')
        response = FileResponse(f, content_type=content_type)
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'
        return response

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', media_serve),
    ]
    # Keep static for completeness (won't be used for media due to earlier re_path)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
