from django import forms
from django.utils.translation import gettext_lazy as _
from jalali_date.widgets import AdminJalaliDateWidget, AdminSplitJalaliDateTime
from .models import Workshop, WorkshopSession


class WorkshopAdminForm(forms.ModelForm):
    """
    Custom form for Workshop admin with Persian date widgets using django-jalali-date
    """
    
    class Meta:
        model = Workshop
        fields = '__all__'
        widgets = {
            'start_date': AdminJalaliDateWidget,          # Persian calendar popup
            'end_date': AdminJalaliDateWidget,            # Persian calendar popup
            'registration_deadline': AdminSplitJalaliDateTime,  # date + time, Persian date
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text for Persian date fields
        self.fields['start_date'].help_text = _('تاریخ شروع کارگاه به شمسی')
        self.fields['end_date'].help_text = _('تاریخ پایان کارگاه به شمسی')
        self.fields['registration_deadline'].help_text = _('مهلت ثبت‌نام به شمسی')


class WorkshopSessionAdminForm(forms.ModelForm):
    """
    Custom form for WorkshopSession admin with Persian date widgets using django-jalali-date
    """
    
    class Meta:
        model = WorkshopSession
        fields = '__all__'
        widgets = {
            'scheduled_datetime': AdminSplitJalaliDateTime,  # date + time, Persian date
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text for Persian date fields
        self.fields['scheduled_datetime'].help_text = _('تاریخ و زمان جلسه به شمسی')
