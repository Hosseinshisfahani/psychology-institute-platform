from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import OTPCode, User
from .sms_service import SmsSendResult, hash_otp


class PasswordResetAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='reset-user@example.com',
            password='OldPass123!',
            first_name='Reset',
            last_name='User',
            phone_number='09123456789',
        )

    def _create_otp(self, code='123456'):
        return OTPCode.objects.create(
            phone_number='09123456789',
            code_hash=hash_otp(code),
            purpose='password_reset',
            expires_at=timezone.now() + timedelta(minutes=3),
        )

    @patch('app.dashboard.api_views.send_otp_sms')
    def test_send_otp_requires_existing_account(self, mock_send):
        mock_send.return_value = SmsSendResult(ok=True, message_id='msg-1')
        response = self.client.post('/api/dashboard/otp/send/', {
            'phone_number': '09999999999',
            'purpose': 'password_reset',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
        mock_send.assert_not_called()

    @patch('app.dashboard.api_views.send_otp_sms')
    def test_send_otp_by_email(self, mock_send):
        mock_send.return_value = SmsSendResult(ok=True, message_id='msg-1')
        response = self.client.post('/api/dashboard/otp/send/', {
            'email': 'reset-user@example.com',
            'purpose': 'password_reset',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data.get('phone_hint'), '0912***89')
        mock_send.assert_called_once()

    def test_reset_password_with_valid_otp(self):
        self._create_otp('654321')
        response = self.client.post('/api/dashboard/password-reset/', {
            'phone_number': '09123456789',
            'otp_code': '654321',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))

    def test_reset_password_rejects_wrong_otp(self):
        self._create_otp('654321')
        response = self.client.post('/api/dashboard/password-reset/', {
            'phone_number': '09123456789',
            'otp_code': '000000',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPass123!'))
