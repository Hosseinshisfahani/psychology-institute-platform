from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from blog.widgets import PersianDateInput

User = get_user_model()


class CustomSignupForm(UserCreationForm):
    """Custom signup form with additional fields"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('نام'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام خود را وارد کنید'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('نام خانوادگی'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام خانوادگی خود را وارد کنید'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label=_('ایمیل'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ایمیل خود را وارد کنید'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label=_('شماره تلفن'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09123456789'
        })
    )
    
    birth_date = forms.DateField(
        required=False,
        label=_('تاریخ تولد'),
        widget=PersianDateInput(attrs={
            'class': 'form-control'
        })
    )
    
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=False,
        label=_('جنسیت'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        required=True,
        label=_('نوع کاربر'),
        initial='client',
        widget=forms.RadioSelect()
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label=_('موافقت با شرایط و قوانین'),
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور خود را وارد کنید'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور را مجدداً وارد کنید'
        })
        
        # Remove username field since we're using email
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('کاربری با این ایمیل قبلاً ثبت‌نام کرده است.'))
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(_('کاربری با این شماره تلفن قبلاً ثبت‌نام کرده است.'))
        return phone_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number')
        user.birth_date = self.cleaned_data.get('birth_date')
        user.gender = self.cleaned_data.get('gender')
        user.user_type = self.cleaned_data.get('user_type', 'client')
        
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """Custom login form for email-based authentication"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rename the username field to email for clarity
        self.fields['username'].label = _('ایمیل')
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ایمیل خود را وارد کنید',
            'autofocus': True,
            'type': 'email'
        })
        
        # Customize the password field
        self.fields['password'].label = _('رمز عبور')
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور خود را وارد کنید'
        })
    
    def clean_username(self):
        """Clean and validate the email field"""
        email = self.cleaned_data.get('username')
        if email:
            email = email.lower().strip()
        return email


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'birth_date', 'gender', 'address', 'city', 'postal_code', 
            'bio', 'profile_image'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': PersianDateInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True  # Email shouldn't be editable
