"""
SMS Service for insms.ir OTP verification
"""
import requests
import random
import logging
from django.conf import settings
from requests.structures import CaseInsensitiveDict

logger = logging.getLogger(__name__)

# SMS API Configuration
SMS_API_URL = "http://smswbs.ir/class/sms/restful"

# Get SMS credentials from settings with validation
SMS_USERNAME = getattr(settings, 'SMS_USERNAME', 'utpsy')
SMS_PASSWORD = getattr(settings, 'SMS_PASSWORD', 'Sarmad@123')
SMS_SENDER_NUMBER = getattr(settings, 'SMS_SENDER_NUMBER', '')

# Log credentials status (without exposing password)
logger.info(f"SMS Config loaded - Username: {SMS_USERNAME}, Sender: {SMS_SENDER_NUMBER}, Password set: {bool(SMS_PASSWORD)}")

# Validate credentials are loaded
if not SMS_USERNAME or not SMS_PASSWORD:
    logger.error(f"SMS credentials not loaded! Username: '{SMS_USERNAME}', Password: {'SET' if SMS_PASSWORD else 'NOT SET'}")

SMS_SEND_OTP_URL = f"{SMS_API_URL}/OTP/send_OTP.php"
SMS_CHECK_OTP_URL = f"{SMS_API_URL}/OTP/check_OTP.php"


def generate_otp_code(length=6):
    """Generate a random OTP code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_sms(phone_number, otp_code):
    logger.info(f"[OTP] Sending to {phone_number} code={otp_code}")

    if not SMS_USERNAME or not SMS_PASSWORD:
        return {'success': False, 'message': 'SMS credentials missing'}

    if not SMS_SENDER_NUMBER:
        logger.error("[OTP] SMS_SENDER_NUMBER is not configured")
        return {'success': False, 'message': 'SMS sender number is not configured. Please set SMS_SENDER_NUMBER in your environment variables.'}

    # Normalize phone
    phone = phone_number.replace("+98", "").replace("0098", "").strip()
    if phone.startswith("0"):
        phone = phone[1:]  # 0912 → 912

    # Normalize sender number - try multiple formats
    sender_raw = SMS_SENDER_NUMBER.replace("+", "").strip()
    
    # Try format 1: Remove country code (9810000101 -> 10000101)
    sender1 = sender_raw.replace("98", "", 1) if sender_raw.startswith("98") else sender_raw
    if sender1.startswith("0"):
        sender1 = sender1[1:]
    
    # Try format 2: Keep country code (9810000101)
    sender2 = sender_raw
    
    # Try format 3: Just the number part (10000101)
    sender3 = sender1
    
    logger.info(f"[OTP] Original sender: {SMS_SENDER_NUMBER}, Formats: {sender1}, {sender2}, {sender3}")

    payload = {
        "uname": SMS_USERNAME,
        "pass": SMS_PASSWORD,
        "to": phone,        # 912xxxxxxx
        "text": f"کد تایید شما: {otp_code}",
        "number": sender2,  # Sender number (سرشماره) - format with country code (9810000101)
        "sender": sender2,   # Also try "sender" as fallback
        "from": sender2,     # Also try "from" as fallback
    }
    
    logger.info(f"[OTP] Payload (without password): { {k: v for k, v in payload.items() if k != 'pass'} }")

    try:
        r = requests.post(
            SMS_SEND_OTP_URL,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        logger.error(f"[OTP] Request error: {e}")
        return {'success': False, 'message': f"Request failed: {e}"}

    logger.info(f"[OTP] Status {r.status_code} Body: {r.text}")

    # --- ALWAYS handle return ---
    # 1) Pure number → success
    if r.text.strip().isdigit():
        return {'success': True, 'message': 'OTP sent', 'transaction_id': r.text.strip()}

    # 2) Try JSON
    try:
        data = r.json()
        if isinstance(data, dict):
            if str(data).lower().find("success") != -1:
                return {'success': True, 'message': 'OTP sent'}
            else:
                # Extract error message
                msg = (
                    data.get("message") or data.get("error") or data.get("result")
                    or str(data)
                )
                return {'success': False, 'message': msg}
    except:
        pass

    # 3) Text success
    if "success" in r.text.lower() or "ok" in r.text.lower():
        return {'success': True, 'message': 'OTP sent'}

    # 4) Otherwise error
    return {'success': False, 'message': r.text[:200]}


def verify_otp_sms(phone_number, otp_code):
    """
    Verify OTP code using insms.ir API
    
    Args:
        phone_number: Phone number in format 09123456789 (without +98)
        otp_code: The OTP code to verify
    
    Returns:
        dict: Response with success status and message
    """
    try:
        # Ensure phone number is in correct format
        phone_number = phone_number.replace('+98', '').replace('0098', '').strip()
        if phone_number.startswith('0'):
            phone_number = phone_number[1:]
        phone_number = f"98{phone_number}"  # Add country code
        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        data = {
            "uname": SMS_USERNAME,
            "pass": SMS_PASSWORD,
            "to": phone_number,
            "otp": otp_code
        }
        
        response = requests.post(
            SMS_CHECK_OTP_URL,
            headers=headers,
            data=data,  # Use data instead of json
            timeout=30
        )
        
        logger.info(f"SMS Verify API Response Status: {response.status_code}")
        logger.info(f"SMS Verify API Response: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict):
                    # Check if verification was successful
                    if result.get('status') == 'success' or result.get('result') == 'success' or 'success' in str(result).lower():
                        return {
                            'success': True,
                            'message': 'OTP verified successfully'
                        }
                    else:
                        error_msg = result.get('message', result.get('error', 'Invalid OTP'))
                        return {
                            'success': False,
                            'message': error_msg
                        }
                else:
                    # If response format is unexpected, check response text
                    if 'success' in response.text.lower() or 'valid' in response.text.lower():
                        return {
                            'success': True,
                            'message': 'OTP verified successfully'
                        }
                    else:
                        return {
                            'success': False,
                            'message': 'Invalid OTP code'
                        }
            except ValueError:
                # Response is not JSON
                if 'success' in response.text.lower() or 'valid' in response.text.lower():
                    return {
                        'success': True,
                        'message': 'OTP verified successfully'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Invalid OTP code'
                    }
        else:
            return {
                'success': False,
                'message': f'SMS service returned status code: {response.status_code}'
            }
            
    except requests.exceptions.Timeout:
        logger.error("SMS Verify API request timed out")
        return {
            'success': False,
            'message': 'SMS service timeout. Please try again later.'
        }
    except requests.exceptions.ConnectionError as e:
        logger.error(f"SMS Verify API connection error: {str(e)}")
        return {
            'success': False,
            'message': 'Failed to connect to SMS service. Please check your internet connection.'
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"SMS Verify API request failed: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to verify OTP: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Unexpected error verifying OTP: {str(e)}")
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }

