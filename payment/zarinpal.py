import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import Payment, Order


class ZarinpalPayment:
    """Zarinpal payment gateway integration"""
    
    def __init__(self):
        self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '')
        self.sandbox = getattr(settings, 'ZARINPAL_SANDBOX', True)
        self.callback_url = getattr(settings, 'ZARINPAL_CALLBACK_URL', '')
        
        if self.sandbox:
            self.request_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'
            self.verify_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'
            self.start_pay_url = 'https://sandbox.zarinpal.com/pg/StartPay/'
        else:
            self.request_url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
            self.verify_url = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
            self.start_pay_url = 'https://www.zarinpal.com/pg/StartPay/'
    
    def create_payment_request(self, order, description="پرداخت سفارش"):
        """Create payment request with Zarinpal"""
        try:
            data = {
                'merchant_id': self.merchant_id,
                'amount': int(order.total_amount),  # Amount in Toman
                'description': description,
                'callback_url': self.callback_url,
                'metadata': {
                    'order_id': order.id,
                    'order_number': order.order_number
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                self.request_url,
                data=json.dumps(data),
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if result.get('data', {}).get('code') == 100:
                authority = result['data']['authority']
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method_id=1,  # Assuming Zarinpal is ID 1
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
            else:
                return {
                    'success': False,
                    'error': result.get('errors', {}).get('message', 'خطا در ایجاد درخواست پرداخت')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'خطا در ارتباط با درگاه پرداخت: {str(e)}'
            }
    
    def verify_payment(self, authority, amount):
        """Verify payment with Zarinpal"""
        try:
            data = {
                'merchant_id': self.merchant_id,
                'amount': int(amount),
                'authority': authority
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                self.verify_url,
                data=json.dumps(data),
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if result.get('data', {}).get('code') == 100:
                return {
                    'success': True,
                    'ref_id': result['data'].get('ref_id'),
                    'card_pan': result['data'].get('card_pan'),
                    'fee': result['data'].get('fee', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('errors', {}).get('message', 'خطا در تایید پرداخت')
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
