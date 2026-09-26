from django.conf import settings
from django.core.exceptions import RequestDataTooBig, TooManyFieldsSent
from django.http import JsonResponse
from django.shortcuts import render
from django.views.defaults import bad_request as django_bad_request


def max_upload_mb(request=None):
    admin_size = getattr(settings, 'ADMIN_UPLOAD_MAX_BYTES', 1000 * 1024 * 1024)
    public_size = getattr(settings, 'PUBLIC_UPLOAD_MAX_BYTES', 100 * 1024 * 1024)
    size = admin_size
    if request is not None:
        path = getattr(request, 'path', '')
        if not (path.startswith('/admin/') or path.startswith('/api/admin/')):
            size = public_size
    return max(1, int(size / (1024 * 1024)))


def admin_upload_mb():
    return max(1, int(getattr(settings, 'ADMIN_UPLOAD_MAX_BYTES', 1000 * 1024 * 1024) / (1024 * 1024)))


def public_upload_mb():
    return max(1, int(getattr(settings, 'PUBLIC_UPLOAD_MAX_BYTES', 100 * 1024 * 1024) / (1024 * 1024)))


def _wants_json(request):
    accept = request.META.get('HTTP_ACCEPT', '')
    return (
        request.path.startswith('/api/')
        or 'application/json' in accept
        or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )


def request_entity_too_large(request, exception=None):
    """Standard Persian 413 page for oversized uploads."""
    limit = max_upload_mb(request)
    if _wants_json(request):
        return JsonResponse(
            {
                'status': 413,
                'error': 'request_entity_too_large',
                'message': (
                    f'حجم درخواست بیش از حد مجاز است. حداکثر حجم مجاز {limit} مگابایت است. '
                    'لطفاً فایل کوچک‌تری انتخاب کنید یا فایل را فشرده نمایید.'
                ),
            },
            status=413,
        )
    return render(
        request,
        'errors/413.html',
        {
            'max_upload_mb': limit,
            'admin_upload_mb': admin_upload_mb(),
            'public_upload_mb': public_upload_mb(),
        },
        status=413,
    )


def bad_request(request, exception):
    if isinstance(exception, RequestDataTooBig):
        return request_entity_too_large(request, exception)
    if isinstance(exception, TooManyFieldsSent):
        if _wants_json(request):
            return JsonResponse(
                {
                    'status': 400,
                    'error': 'too_many_fields',
                    'message': 'تعداد فیلدهای ارسال‌شده بیش از حد مجاز است.',
                },
                status=400,
            )
        return django_bad_request(request, exception)
    if _wants_json(request):
        return JsonResponse(
            {
                'status': 400,
                'error': 'bad_request',
                'message': 'درخواست نامعتبر است.',
            },
            status=400,
        )
    return django_bad_request(request, exception)
