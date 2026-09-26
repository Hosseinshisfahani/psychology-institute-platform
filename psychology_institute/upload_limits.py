from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from psychology_institute.error_views import request_entity_too_large


def _content_length(request):
    try:
        return int(request.META.get('CONTENT_LENGTH') or 0)
    except (TypeError, ValueError):
        return 0


def is_admin_upload_path(path):
    return path.startswith('/admin/') or path.startswith('/api/admin/')


def admin_upload_limit_bytes():
    return int(getattr(settings, 'ADMIN_UPLOAD_MAX_BYTES', 1000 * 1024 * 1024))


def public_upload_limit_bytes():
    return int(getattr(settings, 'PUBLIC_UPLOAD_MAX_BYTES', 100 * 1024 * 1024))


def can_use_admin_upload_limit(request):
    user = getattr(request, 'user', None)
    if user is None or isinstance(user, AnonymousUser):
        return False
    return bool(
        getattr(user, 'is_authenticated', False)
        and (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))
    )


class AdminUploadLimitMiddleware:
    """Allow 1 GB uploads only for staff on admin course/workshop paths."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        content_length = _content_length(request)
        if content_length <= 0:
            return self.get_response(request)

        public_limit = public_upload_limit_bytes()
        if content_length <= public_limit:
            return self.get_response(request)

        admin_limit = admin_upload_limit_bytes()
        if (
            content_length <= admin_limit
            and is_admin_upload_path(request.path)
            and can_use_admin_upload_limit(request)
        ):
            return self.get_response(request)

        return request_entity_too_large(request)
