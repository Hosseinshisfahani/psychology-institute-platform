"""
SMS Service for insms.ir OTP verification
"""
import requests
import random
import logging
import re
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

    # Normalize sender number - keep country code format (9810000101)
    sender = SMS_SENDER_NUMBER.replace("+", "").strip()
    
    logger.info(f"[OTP] Sending from: {sender} to: {phone}")

    payload = {
        "uname": SMS_USERNAME,
        "pass": SMS_PASSWORD,
        "to": phone,        # 912xxxxxxx
        "text": f"کد تایید شما: {otp_code}",
        "from": sender,     # Sender number (must use 'from' field, not 'number' or 'sender')
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
    logger.info(f"[OTP] Response type: {type(r.text)}, length: {len(r.text)}, repr: {repr(r.text[:50])}")

    # Normalize response text
    response_text = r.text.strip() if r.text else ""
    
    # --- ALWAYS handle return ---
    # 1) Try JSON first (some APIs return JSON even for numeric IDs)
    try:
        data = r.json()
        # If JSON parsing succeeds and it's a number, treat as transaction ID
        if isinstance(data, (int, float)):
            transaction_id = str(int(data))
            logger.info(f"[OTP] Detected numeric transaction ID from JSON: {transaction_id}")
            return {'success': True, 'message': 'OTP sent', 'transaction_id': transaction_id}
        elif isinstance(data, dict):
            data_str = str(data)
            if data_str.lower().find("success") != -1:
                return {'success': True, 'message': 'OTP sent'}
            # Some providers return numeric codes inside message/result fields
            possible_code = data.get("message") or data.get("result") or data.get("otp") or data.get("code")
            if isinstance(possible_code, (int, float)):
                transaction_id = str(int(possible_code))
                logger.info(f"[OTP] Detected numeric transaction ID in JSON dict: {transaction_id}")
                return {'success': True, 'message': 'OTP sent', 'transaction_id': transaction_id}
            if isinstance(possible_code, str):
                cleaned_code = possible_code.strip()
                if cleaned_code.isdigit() and len(cleaned_code) >= 4:
                    logger.info(f"[OTP] Detected numeric transaction ID in JSON dict string: {cleaned_code}")
                    return {'success': True, 'message': 'OTP sent', 'transaction_id': cleaned_code}
            # Extract error message
            msg = (
                data.get("message") or data.get("error") or data.get("result")
                or data_str
            )
            return {'success': False, 'message': msg}
        elif isinstance(data, str):
            # If JSON returns a string that's a number, treat as transaction ID
            cleaned_data = data.strip()
            if cleaned_data.isdigit() and len(cleaned_data) >= 6:
                logger.info(f"[OTP] Detected transaction ID from JSON string: {cleaned_data}")
                return {'success': True, 'message': 'OTP sent', 'transaction_id': cleaned_data}
    except (ValueError, TypeError):
        # Not JSON, continue with text parsing
        pass
    
    # 2) Pure number → success (transaction ID)
    # Check if response is a number (with or without whitespace/newlines)
    cleaned_text = response_text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
    if cleaned_text.isdigit() and len(cleaned_text) >= 6:
        logger.info(f"[OTP] Detected transaction ID: {cleaned_text}")
        return {'success': True, 'message': 'OTP sent', 'transaction_id': cleaned_text}
    
    # 3) Also check if it's a number with some prefix/suffix (e.g., "ID:869928146" or "869928146\n")
    number_match = re.search(r'\d{6,}', response_text)  # Match 6+ digit numbers
    if number_match and len(number_match.group()) >= 6:
        # If the response is mostly just a number, treat it as success
        if len(cleaned_text) <= 20 and cleaned_text.replace(number_match.group(), '').strip() == '':
            transaction_id = number_match.group()
            logger.info(f"[OTP] Detected transaction ID in response: {transaction_id}")
            return {'success': True, 'message': 'OTP sent', 'transaction_id': transaction_id}

    # 4) Text success indicators
    response_lower = response_text.lower()
    if "success" in response_lower or "ok" in response_lower or "sent" in response_lower:
        return {'success': True, 'message': 'OTP sent'}

    # 5) Check for known error patterns
    error_patterns = [
        'کد قبلا ارسال شده',
        'already sent',
        'error',
        'fail',
        'invalid',
    ]
    if any(pattern in response_lower for pattern in error_patterns):
        return {'success': False, 'message': response_text[:200]}
    
    # 6) If response is short and looks like a number, treat as success
    if len(cleaned_text) <= 20 and cleaned_text.replace(' ', '').isdigit():
        logger.info(f"[OTP] Treating short numeric response as transaction ID: {cleaned_text}")
        return {'success': True, 'message': 'OTP sent', 'transaction_id': cleaned_text.replace(' ', '')}

    # 7) Otherwise error
    logger.warning(f"[OTP] Unrecognized response format, treating as error: {response_text[:200]}")
    return {'success': False, 'message': response_text[:200]}


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

