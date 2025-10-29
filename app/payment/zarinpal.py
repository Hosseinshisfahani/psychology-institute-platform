import requests
from django.conf import settings
from django.utils import timezone
from .models import Payment, Order, PaymentMethod


class ZarinpalPayment:
    """Zarinpal payment gateway integration"""
    
    def __init__(self):
        self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '')
        self.sandbox = getattr(settings, 'ZARINPAL_SANDBOX', True)
        
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
    
    def create_payment_request(self, order, description="پرداخت سفارش"):
        """Create payment request with Zarinpal"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.merchant_id:
            logger.error('Zarinpal merchant ID is not configured')
            return {
                'success': False,
                'error': 'Merchant ID تنظیم نشده است'
            }
        
        # Log payment request details (without full merchant ID for security)
        logger.info(
            f'Creating Zarinpal payment request: Order {order.id}, '
            f'Amount: {order.total_amount}, API Version: {self.api_version}, '
            f'Sandbox: {self.sandbox}, Callback: {self.callback_url}, '
            f'Merchant ID: {self.merchant_id[:8]}...'
        )
        
        try:
            # Prepare request data based on API version
            if self.api_version == 4:
                # Zarinpal API v4 format
                data = {
                    'merchant_id': self.merchant_id,
                    'amount': int(order.total_amount * 10),  # API v4 uses Rials (amount * 10)
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
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total_amount,
                gateway_transaction_id=authority,
                gateway_response=result,
                status='pending'
            )
            
            return {
                'success': True,
                'authority': authority,
                'payment_url': f"{self.start_pay_url}{authority}",
                'payment_id': payment.id
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
                    'amount': int(amount * 10),  # API v4 uses Rials
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
