from django import forms
from django.forms.widgets import DateInput, TextInput
import jdatetime
from datetime import datetime


class PersianDateInput(TextInput):
    """
    Custom widget for Persian date input using Persian date picker
    """
    input_type = 'text'
    
    def __init__(self, attrs=None, format='%Y/%m/%d'):
        default_attrs = {
            'class': 'form-control persian-date-picker',
            'placeholder': 'مثال: ۱۴۰۳/۰۷/۰۱',
            'autocomplete': 'off',
            'readonly': True,
        }
        if attrs:
            default_attrs.update(attrs)
        self.format = format
        super().__init__(attrs=default_attrs)

    def format_value(self, value):
        """Convert Gregorian date to Persian format for display"""
        if value is None:
            return ''
        
        if isinstance(value, str):
            try:
                # Try to parse the string as a date
                if '/' in value:
                    # Already in Persian format
                    return value
                else:
                    # Parse as ISO format
                    value = datetime.strptime(value, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return value
        
        if hasattr(value, 'year'):
            # Convert Gregorian to Jalali
            jalali_date = jdatetime.date.fromgregorian(date=value)
            # Format with Persian numbers
            formatted = f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
            
            # Convert to Persian numbers
            persian_digits = '۰۱۲۳۴۵۶۷۸۹'
            english_digits = '0123456789'
            
            for i, digit in enumerate(english_digits):
                formatted = formatted.replace(digit, persian_digits[i])
            
            return formatted
        
        return value

    def value_from_datadict(self, data, files, name):
        """Convert Persian date input to Gregorian format for storage"""
        value = data.get(name)
        if not value:
            return None
        
        try:
            # Convert Persian numbers to English
            english_digits = '0123456789'
            persian_digits = '۰۱۲۳۴۵۶۷۸۹'
            
            for i, digit in enumerate(persian_digits):
                value = value.replace(digit, english_digits[i])
            
            # Parse Persian date
            if '/' in value:
                parts = value.split('/')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    # Convert from Jalali to Gregorian
                    jalali_date = jdatetime.date(year, month, day)
                    gregorian_date = jalali_date.togregorian()
                    return gregorian_date.strftime('%Y-%m-%d')
            
            return value
        except (ValueError, TypeError, AttributeError):
            return value

    class Media:
        css = {
            'all': ('css/persian-datepicker.css',)
        }
        js = ('js/persian-datepicker.js',)


class PersianDateTimeInput(TextInput):
    """
    Custom widget for Persian datetime input
    """
    input_type = 'text'
    
    def __init__(self, attrs=None, format='%Y/%m/%d %H:%M'):
        default_attrs = {
            'class': 'form-control persian-datetime-picker',
            'placeholder': 'مثال: ۱۴۰۳/۰۷/۰۱ ۱۴:۳۰',
            'autocomplete': 'off',
            'readonly': True,
        }
        if attrs:
            default_attrs.update(attrs)
        self.format = format
        super().__init__(attrs=default_attrs)

    def format_value(self, value):
        """Convert Gregorian datetime to Persian format for display"""
        if value is None:
            return ''
        
        if isinstance(value, str):
            try:
                if '/' in value and len(value.split()) > 1:
                    return value  # Already in Persian format
                else:
                    value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                return value
        
        if hasattr(value, 'year'):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
            formatted = f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d} {jalali_date.hour:02d}:{jalali_date.minute:02d}"
            
            # Convert to Persian numbers
            persian_digits = '۰۱۲۳۴۵۶۷۸۹'
            english_digits = '0123456789'
            
            for i, digit in enumerate(english_digits):
                formatted = formatted.replace(digit, persian_digits[i])
            
            return formatted
        
        return value

    def value_from_datadict(self, data, files, name):
        """Convert Persian datetime input to Gregorian format for storage"""
        value = data.get(name)
        if not value:
            return None
        
        try:
            # Convert Persian numbers to English
            english_digits = '0123456789'
            persian_digits = '۰۱۲۳۴۵۶۷۸۹'
            
            for i, digit in enumerate(persian_digits):
                value = value.replace(digit, english_digits[i])
            
            # Parse Persian datetime
            if '/' in value and ' ' in value:
                date_part, time_part = value.split(' ', 1)
                date_parts = date_part.split('/')
                time_parts = time_part.split(':')
                
                if len(date_parts) == 3 and len(time_parts) >= 2:
                    year, month, day = map(int, date_parts)
                    hour, minute = map(int, time_parts[:2])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    
                    jalali_date = jdatetime.datetime(year, month, day, hour, minute, second)
                    gregorian_date = jalali_date.togregorian()
                    return gregorian_date.strftime('%Y-%m-%d %H:%M:%S')
            
            return value
        except (ValueError, TypeError, AttributeError):
            return value

    class Media:
        css = {
            'all': ('css/persian-datepicker.css',)
        }
        js = ('js/persian-datepicker.js',)
