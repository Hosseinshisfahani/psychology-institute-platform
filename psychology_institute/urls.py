
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import JsonResponse, FileResponse, StreamingHttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
import os
import re
import mimetypes
from urllib.parse import unquote

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

# CSRF token endpoint for SPA frontends
@require_http_methods(["GET"])
@ensure_csrf_cookie
def csrf_token_view(request):
    """CSRF token endpoint with CORS support"""
    response = JsonResponse({'csrfToken': get_token(request)})
    # Explicitly add CORS headers
    origin = request.META.get('HTTP_ORIGIN')
    if origin:
        from django.conf import settings
        if hasattr(settings, 'CORS_ALLOWED_ORIGINS') and origin in settings.CORS_ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
        elif getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False):
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
    return response

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Admin
    path('admin/', admin.site.urls),

    # CSRF token endpoint for SPA frontends
    path('csrf/', csrf_token_view, name='csrf_token'),
    
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
    path('api/mmpi/', include('app.mmpi.api_urls')),
    
    # Redirect root to React frontend
    path('', RedirectView.as_view(url='http://localhost:3000', permanent=False), name='home_redirect'),
    
    # Apps (for API endpoints only)
    path('blog/', include('app.blog.urls')),
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
    path('mmpi/', include('app.mmpi.urls')),
]

# Static files are now served by nginx (see /etc/nginx/sites-available/psychology-institute)
# Only serve static files in DEBUG/development mode as a fallback
if settings.DEBUG or getattr(settings, "DEVELOPMENT_MODE", False):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files - Always use custom handler for proper URL decoding and range support
# Range-supporting media handler for seeking video/audio
def media_serve(request, path):
    # Decode URL-encoded path (important for Persian/Arabic filenames)
    decoded_path = unquote(path)
    full_path = os.path.join(settings.MEDIA_ROOT, decoded_path)
    
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

# Always use custom media handler (works in both DEBUG and production)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', media_serve),
]

# Serve frontend public images in DEBUG/development mode.
# Production serves /images via nginx.
def images_serve(request, path):
    decoded_path = unquote(path)
    images_root = os.path.join(str(settings.BASE_DIR), 'frontend', 'public', 'images')
    full_path = os.path.join(images_root, decoded_path)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise Http404()

    content_type, _ = mimetypes.guess_type(full_path)
    content_type = content_type or 'application/octet-stream'
    return FileResponse(open(full_path, 'rb'), content_type=content_type)

if settings.DEBUG or getattr(settings, "DEVELOPMENT_MODE", False):
    urlpatterns += [
        re_path(r'^images/(?P<path>.*)$', images_serve),
    ]
