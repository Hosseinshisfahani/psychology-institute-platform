from django import forms
from django.contrib.auth import get_user_model
from .models import Session, SessionType, SessionRating, SessionCancellation

User = get_user_model()


class SessionBookingForm(forms.ModelForm):
    """Form for booking therapy sessions"""
    
    class Meta:
        model = Session
        fields = ['therapist', 'session_type', 'scheduled_date', 'scheduled_time', 'mode', 'location']
        widgets = {
            'therapist': forms.Select(attrs={'class': 'form-select'}),
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'آدرس یا مکان جلسه (اختیاری)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['therapist'].queryset = User.objects.filter(
            user_type='therapist', 
            is_active=True, 
            is_available=True
        ).order_by('first_name', 'last_name')
        self.fields['session_type'].queryset = SessionType.objects.filter(is_active=True)
        
        # Set labels
        self.fields['therapist'].label = 'درمانگر'
        self.fields['session_type'].label = 'نوع جلسه'
        self.fields['scheduled_date'].label = 'تاریخ جلسه'
        self.fields['scheduled_time'].label = 'زمان جلسه'
        self.fields['mode'].label = 'نحوه برگزاری'
        self.fields['location'].label = 'مکان (اختیاری)'
    
    def clean_scheduled_date(self):
        from django.utils import timezone
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now().date():
            raise forms.ValidationError('تاریخ جلسه نمی‌تواند در گذشته باشد.')
        return scheduled_date


class SessionRescheduleForm(forms.ModelForm):
    """Form for rescheduling sessions"""
    
    class Meta:
        model = Session
        fields = ['scheduled_date', 'scheduled_time']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_date'].label = 'تاریخ جدید'
        self.fields['scheduled_time'].label = 'زمان جدید'
    
    def clean_scheduled_date(self):
        from django.utils import timezone
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now().date():
            raise forms.ValidationError('تاریخ جلسه نمی‌تواند در گذشته باشد.')
        return scheduled_date


class SessionRatingForm(forms.ModelForm):
    """Form for rating sessions"""
    
    class Meta:
        model = SessionRating
        fields = ['overall_rating', 'therapist_rating', 'environment_rating', 'helpfulness_rating', 'comments', 'would_recommend']
        widgets = {
            'overall_rating': forms.HiddenInput(),
            'therapist_rating': forms.HiddenInput(),
            'environment_rating': forms.HiddenInput(),
            'helpfulness_rating': forms.HiddenInput(),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'نظرات خود را بنویسید...'}),
            'would_recommend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comments'].label = 'نظرات و پیشنهادات'
        self.fields['would_recommend'].label = 'آیا این درمانگر را به دیگران توصیه می‌کنید؟'


class SessionCancellationForm(forms.ModelForm):
    """Form for cancelling sessions"""
    
    class Meta:
        model = SessionCancellation
        fields = ['reason', 'explanation']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'توضیح بیشتری در مورد دلیل لغو جلسه...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].label = 'دلیل لغو'
        self.fields['explanation'].label = 'توضیحات (اختیاری)'


class TherapistAvailabilityForm(forms.Form):
    """Form for managing therapist availability"""
    
    day_of_week = forms.ChoiceField(
        choices=[
            ('monday', 'دوشنبه'),
            ('tuesday', 'سه‌شنبه'),
            ('wednesday', 'چهارشنبه'),
            ('thursday', 'پنج‌شنبه'),
            ('friday', 'جمعه'),
            ('saturday', 'شنبه'),
            ('sunday', 'یکشنبه'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='روز هفته'
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='ساعت شروع'
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='ساعت پایان'
    )
    is_available = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='در دسترس'
    )