from django import template
from django.utils import timezone
import jdatetime
from datetime import datetime

register = template.Library()

# Persian month names
PERSIAN_MONTHS = [
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
]

# Persian day names
PERSIAN_DAYS = [
    'شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه'
]

def to_jalali_date(date_obj, format_string='Y/m/d'):
    """
    Convert a datetime object to Jalali date format
    """
    if not date_obj:
        return ''
    
    # Handle timezone-aware datetime objects
    if timezone.is_aware(date_obj):
        date_obj = timezone.localtime(date_obj)
    
    # Convert to Jalali
    jalali_date = jdatetime.datetime.fromgregorian(datetime=date_obj)
    
    # Format the date
    if format_string == 'Y/m/d':
        return f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"
    elif format_string == 'Y/m/d H:i':
        return f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d} {jalali_date.hour:02d}:{jalali_date.minute:02d}"
    elif format_string == 'j F Y':
        month_name = PERSIAN_MONTHS[jalali_date.month - 1]
        return f"{jalali_date.day} {month_name} {jalali_date.year}"
    elif format_string == 'l j F Y':
        day_name = PERSIAN_DAYS[jalali_date.weekday()]
        month_name = PERSIAN_MONTHS[jalali_date.month - 1]
        return f"{day_name} {jalali_date.day} {month_name} {jalali_date.year}"
    elif format_string == 'F Y':
        month_name = PERSIAN_MONTHS[jalali_date.month - 1]
        return f"{month_name} {jalali_date.year}"
    elif format_string == 'j F':
        month_name = PERSIAN_MONTHS[jalali_date.month - 1]
        return f"{jalali_date.day} {month_name}"
    elif format_string == 'H:i':
        return f"{jalali_date.hour:02d}:{jalali_date.minute:02d}"
    else:
        # Default format
        return f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"

def to_jalali_time(date_obj, format_string='H:i'):
    """
    Convert a datetime object to Jalali time format
    """
    if not date_obj:
        return ''
    
    # Handle timezone-aware datetime objects
    if timezone.is_aware(date_obj):
        date_obj = timezone.localtime(date_obj)
    
    # Convert to Jalali
    jalali_date = jdatetime.datetime.fromgregorian(datetime=date_obj)
    
    if format_string == 'H:i':
        return f"{jalali_date.hour:02d}:{jalali_date.minute:02d}"
    elif format_string == 'H:i:s':
        return f"{jalali_date.hour:02d}:{jalali_date.minute:02d}:{jalali_date.second:02d}"
    else:
        return f"{jalali_date.hour:02d}:{jalali_date.minute:02d}"

def jalali_date(date_obj, format_string='Y/m/d'):
    """
    Main filter for converting dates to Jalali format
    """
    return to_jalali_date(date_obj, format_string)

def jalali_time(date_obj, format_string='H:i'):
    """
    Filter for converting time to Jalali format
    """
    return to_jalali_time(date_obj, format_string)

def persian_number(number):
    """
    Convert English numbers to Persian numbers
    """
    if number is None:
        return ''
    
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    
    number_str = str(number)
    for i, digit in enumerate(english_digits):
        number_str = number_str.replace(digit, persian_digits[i])
    
    return number_str

def jalali_date_persian(date_obj, format_string='Y/m/d'):
    """
    Convert date to Jalali format with Persian numbers
    """
    jalali_str = to_jalali_date(date_obj, format_string)
    return persian_number(jalali_str)

def jalali_time_persian(date_obj, format_string='H:i'):
    """
    Convert time to Jalali format with Persian numbers
    """
    jalali_str = to_jalali_time(date_obj, format_string)
    return persian_number(jalali_str)

# Register the filters
register.filter('jalali_date', jalali_date)
register.filter('jalali_time', jalali_time)
register.filter('jalali_date_persian', jalali_date_persian)
register.filter('jalali_time_persian', jalali_time_persian)
register.filter('persian_number', persian_number)
