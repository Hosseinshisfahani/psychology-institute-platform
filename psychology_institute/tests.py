import json

from django.core.exceptions import RequestDataTooBig
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse

from psychology_institute.error_views import bad_request, request_entity_too_large


@override_settings(SECURE_SSL_REDIRECT=False)
class Error413Tests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_html_413_page_is_persian(self):
        request = self.factory.get('/admin/courses/course/add/')
        response = request_entity_too_large(request)
        self.assertEqual(response.status_code, 413)
        content = response.content.decode('utf-8')
        self.assertIn('lang="fa"', content)
        self.assertIn('dir="rtl"', content)
        self.assertIn('حجم فایل بیش از حد مجاز است', content)
        self.assertIn('بازگشت به افزودن دوره', content)

    def test_json_413_for_api_clients(self):
        request = self.factory.post('/api/courses/', HTTP_ACCEPT='application/json')
        response = request_entity_too_large(request)
        self.assertEqual(response.status_code, 413)
        payload = json.loads(response.content.decode('utf-8'))
        self.assertEqual(payload['error'], 'request_entity_too_large')
        self.assertIn('حجم درخواست', payload['message'])

    def test_bad_request_maps_request_data_too_big_to_413(self):
        request = self.factory.post('/admin/courses/course/add/')
        response = bad_request(request, RequestDataTooBig())
        self.assertEqual(response.status_code, 413)

    def test_named_413_url_renders_persian_page(self):
        response = self.client.get(reverse('error_413'), secure=True)
        self.assertEqual(response.status_code, 413)
        self.assertContains(response, 'حجم فایل بیش از حد مجاز است', status_code=413)


class AdminUploadLimitTests(SimpleTestCase):
    def setUp(self):
        from django.http import HttpResponse
        from psychology_institute.upload_limits import AdminUploadLimitMiddleware

        self.factory = RequestFactory()

        def ok(_request):
            return HttpResponse('ok')

        self.middleware = AdminUploadLimitMiddleware(ok)

    def _post(self, path, size, user):
        request = self.factory.post(path, CONTENT_LENGTH=str(size))
        request.user = user
        return self.middleware(request)

    def test_staff_can_upload_500mb_on_admin_course_path(self):
        user = type('User', (), {'is_authenticated': True, 'is_staff': True, 'is_superuser': False})()
        response = self._post('/admin/courses/course/add/', 500 * 1024 * 1024, user)
        self.assertEqual(response.status_code, 200)

    def test_staff_can_upload_500mb_on_admin_workshop_api(self):
        user = type('User', (), {'is_authenticated': True, 'is_staff': True, 'is_superuser': False})()
        response = self._post('/api/admin/workshops/', 500 * 1024 * 1024, user)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_cannot_upload_200mb_on_admin(self):
        from django.contrib.auth.models import AnonymousUser

        response = self._post('/admin/courses/course/add/', 200 * 1024 * 1024, AnonymousUser())
        self.assertEqual(response.status_code, 413)

    def test_public_api_rejects_200mb(self):
        user = type('User', (), {'is_authenticated': True, 'is_staff': True, 'is_superuser': True})()
        response = self._post('/api/courses/', 200 * 1024 * 1024, user)
        self.assertEqual(response.status_code, 413)

    def test_over_1gb_rejected_even_for_staff(self):
        user = type('User', (), {'is_authenticated': True, 'is_staff': True, 'is_superuser': True})()
        response = self._post('/admin/courses/course/add/', 1001 * 1024 * 1024, user)
        self.assertEqual(response.status_code, 413)


class AdminPersianErrorTests(SimpleTestCase):
    def test_admin_form_error_banner_is_persian(self):
        from django.utils.translation import activate, ngettext

        activate('fa')
        message = ngettext(
            'Please correct the error below.',
            'Please correct the errors below.',
            1,
        )
        self.assertEqual(message, 'لطفاً خطای زیر را اصلاح کنید.')
