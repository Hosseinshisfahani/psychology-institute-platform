import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from .models import Payment, Order, PaymentMethod


class ZarinpalPayment:
    """Zarinpal payment gateway integration"""
    
    def __init__(self):
        self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '')
        self.sandbox = getattr(settings, 'ZARINPAL_SANDBOX', True)
        self.authority_timeout_minutes = getattr(
            settings,
            'ZARINPAL_AUTHORITY_EXPIRATION_MINUTES',
            10
        )
        
        # Get callback URL from settings or construct it
        callback_url = getattr(settings, 'ZARINPAL_CALLBACK_URL', '')
        if not callback_url:
            # Auto-construct callback URL based on site URL
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            callback_url = f"{site_url}/api/payment/verify/"
        self.callback_url = callback_url
        
        # Zarinpal API URLs
        # Zarinpal now uses v4 API for both sandbox and production
        # The old v3 WebGate API has been deprecated
        if self.sandbox:
            self.request_url = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
            self.verify_url = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
            self.start_pay_url = 'https://sandbox.zarinpal.com/pg/StartPay/'
            self.api_version = 4
        else:
            self.request_url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
            self.verify_url = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
            self.start_pay_url = 'https://www.zarinpal.com/pg/StartPay/'
            self.api_version = 4
    
    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _normalize_amount(self, amount):
        """Normalize decimal amount to whole Toman using half-up rounding"""
        if amount is None:
            return Decimal('0')
        try:
            decimal_amount = Decimal(str(amount))
        except (InvalidOperation, TypeError):
            return Decimal('0')
        return decimal_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    def _amount_to_rials(self, amount):
        """Convert Toman amount to rial integer value as expected by v4 API"""
        normalized = self._normalize_amount(amount)
        return int(normalized * 10)
    
    def get_start_pay_url(self, authority):
        """Build StartPay URL for a given authority"""
        authority = (authority or '').strip()
        return f"{self.start_pay_url}{authority}"
    
    def calculate_authority_expiry(self, reference_time=None):
        """Calculate expiry datetime for an authority"""
        reference_time = reference_time or timezone.now()
        return reference_time + timedelta(minutes=self.authority_timeout_minutes)
    
    def is_authority_expired(self, payment):
        """Return True if the stored authority is expired"""
        if not payment or not payment.gateway_transaction_id:
            return True
        if not payment.created_at:
            return True
        return timezone.now() >= self.calculate_authority_expiry(payment.created_at)
    
    def extract_payment_url(self, payment):
        """Extract stored payment URL or rebuild it from authority"""
        if not payment:
            return None
        response = payment.gateway_response or {}
        data = response.get('data')
        if isinstance(data, dict):
            url = data.get('payment_url')
            if url:
                return url
        return self.get_start_pay_url(payment.gateway_transaction_id) if payment.gateway_transaction_id else None
    
    def extract_payment_expiry(self, payment):
        """Extract stored expiry timestamp or compute one"""
        if not payment:
            return None
        response = payment.gateway_response or {}
        data = response.get('data')
        if isinstance(data, dict):
            expires_at = data.get('expires_at')
            if expires_at:
                return expires_at
        if payment.created_at:
            expiry_dt = self.calculate_authority_expiry(payment.created_at)
            return expiry_dt.isoformat()
        return None
    
    def mark_payment_expired(self, payment):
        """Mark a pending payment as expired/failed"""
        if not payment:
            return
        response = payment.gateway_response or {}
        timestamp = timezone.now().isoformat()
        data = response.get('data')
        if isinstance(data, dict):
            data['authority_expired'] = True
            data['authority_expired_at'] = timestamp
            response['data'] = data
        else:
            response['authority_expired'] = True
            response['authority_expired_at'] = timestamp
        payment.gateway_response = response
        payment.status = 'failed'
        payment.save(update_fields=['status', 'gateway_response'])
    
    def _get_payment_method(self):
        """Get or create Zarinpal payment method"""
        payment_method, created = PaymentMethod.objects.get_or_create(
            payment_type='zarinpal',
            defaults={
                'name': 'زرین پال',
                'is_active': True
            }
        )
        return payment_method
    
    def create_payment_request(self, order, description="پرداخت سفارش", frontend_url=None):
        """Create payment request with Zarinpal"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.merchant_id:
            logger.error('Zarinpal merchant ID is not configured')
            return {
                'success': False,
                'error': 'Merchant ID تنظیم نشده است'
            }
        
        amount_toman = self._normalize_amount(getattr(order, 'total_amount', None))
        if amount_toman <= 0:
            logger.error('Attempted to create payment request with non-positive amount', extra={'order_id': order.id})
            return {
                'success': False,
                'error': 'مبلغ سفارش نامعتبر است'
            }
        
        # Log payment request details (without full merchant ID for security)
        logger.info(
            f'Creating Zarinpal payment request: Order {order.id}, '
            f'Amount: {amount_toman}, API Version: {self.api_version}, '
            f'Sandbox: {self.sandbox}, Callback: {self.callback_url}, '
            f'Merchant ID: {self.merchant_id[:8]}...'
        )
        
        try:
            # Prepare request data based on API version
            if self.api_version == 4:
                # Zarinpal API v4 format
                data = {
                    'merchant_id': self.merchant_id,
                    'amount': self._amount_to_rials(amount_toman),  # API v4 uses Rials (amount * 10)
                    'description': description,
                    'callback_url': self.callback_url,
                    'metadata': {
                        'order_id': str(order.id),
                        'order_number': order.order_number
                    }
                }
            else:
                # Zarinpal API v3 (sandbox) format
                data = {
                    'MerchantID': self.merchant_id,
                    'Amount': int(order.total_amount),  # v3 uses Toman
                    'Description': description,
                    'CallbackURL': self.callback_url
                }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                self.request_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            # Check response status code first
            if response.status_code != 200:
                logger.error(
                    f'Zarinpal API returned non-200 status: {response.status_code}. '
                    f'Response: {response.text[:500]}'
                )
                return {
                    'success': False,
                    'error': f'خطا در ارتباط با درگاه: کد پاسخ {response.status_code}',
                    'details': response.text[:500]  # First 500 chars of response
                }
            
            try:
                result = response.json()
                logger.debug(f'Zarinpal API response: {result}')
            except ValueError as e:
                logger.error(f'Failed to parse Zarinpal JSON response: {e}. Response text: {response.text[:500]}')
                return {
                    'success': False,
                    'error': 'پاسخ نامعتبر از درگاه پرداخت',
                    'details': response.text[:500]
                }
            
            # Handle response based on API version
            if self.api_version == 4:
                if result.get('data') and result['data'].get('code') == 100:
                    authority = result['data']['authority']
                else:
                    # Better error extraction for v4
                    errors = result.get('errors', {})
                    if isinstance(errors, dict):
                        error_message = errors.get('message', '')
                        if not error_message:
                            # Try to get any error message from the errors dict
                            error_message = str(errors) if errors else 'خطا در ایجاد درخواست پرداخت'
                    else:
                        error_message = str(errors) if errors else 'خطا در ایجاد درخواست پرداخت'
                    
                    # Include status code if available
                    status_code = result.get('errors', {}).get('code', '')
                    if status_code:
                        error_message = f"{error_message} (کد خطا: {status_code})"
                    
                    return {
                        'success': False,
                        'error': error_message,
                        'details': result
                    }
            else:
                # API v3 response format
                if result.get('Status') == 100:
                    authority = result['Authority']
                else:
                    error_message = result.get('Message', 'خطا در ایجاد درخواست پرداخت')
                    status_code = result.get('Status', '')
                    if status_code:
                        error_message = f"{error_message} (کد خطا: {status_code})"
                    logger.error(
                        f'Zarinpal v3 payment request failed: {error_message}. '
                        f'Status: {status_code}, Full response: {result}'
                    )
                    return {
                        'success': False,
                        'error': error_message,
                        'details': result
                    }
            
            # Get or create payment method
            payment_method = self._get_payment_method()
            
            # Store frontend URL in result if provided
            if frontend_url:
                if isinstance(result, dict):
                    if 'data' not in result:
                        result['data'] = {}
                    result['data']['frontend_url'] = frontend_url
                else:
                    result = {'data': {'frontend_url': frontend_url}, **result}
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total_amount,
                gateway_transaction_id=authority,
                gateway_response=result,
                status='pending'
            )
            
            issued_at = timezone.now()
            expires_at = self.calculate_authority_expiry(issued_at)
            payment_url = self.get_start_pay_url(authority)
            
            # Augment result payload with helpful metadata
            data_section = result.get('data') if isinstance(result, dict) else {}
            if isinstance(data_section, dict):
                data_section.setdefault('authority', authority)
                data_section['issued_at'] = issued_at.isoformat()
                data_section['expires_at'] = expires_at.isoformat()
                data_section['payment_url'] = payment_url
                if frontend_url:
                    data_section['frontend_url'] = frontend_url
                result['data'] = data_section
                payment.gateway_response = result
                payment.save(update_fields=['gateway_response'])
            
            return {
                'success': True,
                'authority': authority,
                'payment_url': payment_url,
                'payment_id': payment.id,
                'expires_at': expires_at.isoformat()
            }
                
        except requests.RequestException as e:
            logger.exception(f'Zarinpal API request exception: {e}')
            return {
                'success': False,
                'error': f'خطا در ارتباط با درگاه پرداخت: {str(e)}',
                'details': {'exception_type': type(e).__name__, 'exception_message': str(e)}
            }
        except Exception as e:
            logger.exception(f'Unexpected error creating Zarinpal payment request: {e}')
            return {
                'success': False,
                'error': f'خطا در پردازش درخواست: {str(e)}',
                'details': {'exception_type': type(e).__name__, 'exception_message': str(e)}
            }
    
    def verify_payment(self, authority, amount):
        """Verify payment with Zarinpal"""
        if not self.merchant_id:
            return {
                'success': False,
                'error': 'Merchant ID تنظیم نشده است'
            }
        
        try:
            # Prepare verification data based on API version
            if self.api_version == 4:
                data = {
                    'merchant_id': self.merchant_id,
                    'amount': self._amount_to_rials(amount),  # API v4 uses Rials
                    'authority': authority
                }
            else:
                # API v3 format
                data = {
                    'MerchantID': self.merchant_id,
                    'Amount': int(amount),  # v3 uses Toman
                    'Authority': authority
                }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                self.verify_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            # Handle response based on API version
            if self.api_version == 4:
                if result.get('data') and result['data'].get('code') == 100:
                    return {
                        'success': True,
                        'ref_id': result['data'].get('ref_id'),
                        'card_pan': result['data'].get('card_pan'),
                        'card_hash': result['data'].get('card_hash'),
                        'fee': result['data'].get('fee', 0),
                        'fee_type': result['data'].get('fee_type')
                    }
                else:
                    error_message = result.get('errors', {}).get('message', 'خطا در تایید پرداخت')
                    if not error_message:
                        error_message = str(result.get('errors', {}))
                    return {
                        'success': False,
                        'error': error_message
                    }
            else:
                # API v3 response format
                if result.get('Status') == 100:
                    return {
                        'success': True,
                        'ref_id': result.get('RefID'),
                        'fee': 0
                    }
                else:
                    error_message = result.get('Message', 'خطا در تایید پرداخت')
                    return {
                        'success': False,
                        'error': error_message
                    }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'خطا در ارتباط با درگاه پرداخت: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'خطا در تایید پرداخت: {str(e)}'
            }
    
    def get_payment_status(self, authority):
        """Get payment status from Zarinpal"""
        try:
            # This would require additional API call to Zarinpal
            # For now, we'll return a basic status check
            return {
                'success': True,
                'status': 'pending'  # This should be determined by actual API call
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'خطا در بررسی وضعیت پرداخت: {str(e)}'
            }
