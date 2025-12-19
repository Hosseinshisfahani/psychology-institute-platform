from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Extended User model with additional fields for psychology institute"""
    
    objects = UserManager()
    
    USER_TYPES = [
        ('client', _('Client')),
        ('therapist', _('Therapist')),
        ('admin', _('Administrator')),
        ('staff', _('Staff')),
    ]
    
    GENDER_CHOICES = [
        ('M', _('آقای')),
        ('F', _('خانم')),
    ]
    
    # Remove username field since we're using email-based authentication
    username = None
    email = models.EmailField(_('آدرس ایمیل'), unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='client', verbose_name='نوع کاربر')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='شماره تلفن')
    first_name_en = models.CharField(max_length=150, blank=True, null=True, verbose_name='نام لاتین')
    last_name_en = models.CharField(max_length=150, blank=True, null=True, verbose_name='نام خانوادگی لاتین')
    national_id = models.CharField(max_length=10, blank=True, null=True, unique=True, verbose_name='کد ملی')
    birth_date = models.DateField(blank=True, null=True, verbose_name='تاریخ تولد')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='جنسیت')
    address = models.TextField(blank=True, null=True, verbose_name='آدرس')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='شهر')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='کد پستی')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='تصویر پروفایل')
    bio = models.TextField(blank=True, null=True, verbose_name='بیوگرافی')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    # Therapist specific fields
    license_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='شماره مجوز')
    specialization = models.CharField(max_length=200, blank=True, null=True, verbose_name='تخصص')
    experience_years = models.PositiveIntegerField(default=0, verbose_name='سال‌های تجربه')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='نرخ ساعتی')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    """Additional profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='کاربر')
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='نام تماس اضطراری')
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='تلفن تماس اضطراری')
    medical_conditions = models.TextField(blank=True, null=True, verbose_name='شرایط پزشکی')
    medications = models.TextField(blank=True, null=True, verbose_name='داروها')
    therapy_goals = models.TextField(blank=True, null=True, verbose_name='اهداف درمانی')
    preferred_language = models.CharField(max_length=10, default='fa', verbose_name='زبان ترجیحی')
    timezone = models.CharField(max_length=50, default='Asia/Tehran', verbose_name='منطقه زمانی')
    notification_preferences = models.JSONField(default=dict, verbose_name='ترجیحات اعلان')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('پروفایل کاربر')
        verbose_name_plural = _('پروفایل‌های کاربر')
    
    def __str__(self):
        return f"Profile for {self.user.full_name}"


class Activity(models.Model):
    """User activity tracking"""
    
    ACTIVITY_TYPES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('course_enrollment', _('Course Enrollment')),
        ('session_booking', _('Session Booking')),
        ('payment', _('Payment')),
        ('profile_update', _('Profile Update')),
        ('other', _('Other')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', verbose_name='کاربر')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, verbose_name='نوع فعالیت')
    description = models.TextField(verbose_name='توضیحات')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='آدرس IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='مرورگر کاربر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('فعالیت')
        verbose_name_plural = _('فعالیت‌ها')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_activity_type_display()}"


class Notification(models.Model):
    """User notifications system"""
    
    NOTIFICATION_TYPES = [
        ('info', _('Information')),
        ('success', _('Success')),
        ('warning', _('Warning')),
        ('error', _('Error')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='کاربر')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    message = models.TextField(verbose_name='پیام')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name='نوع اعلان')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('اعلان')
        verbose_name_plural = _('اعلان‌ها')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.full_name}"


class OTPCode(models.Model):
    """OTP code for SMS verification"""
    
    phone_number = models.CharField(max_length=15, verbose_name='شماره تلفن')
    code = models.CharField(max_length=10, verbose_name='کد تایید', blank=True, null=True)
    transaction_id = models.CharField(max_length=50, verbose_name='شناسه تراکنش', blank=True, null=True, help_text='Transaction ID from SMS provider')
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('signup', _('ثبت‌نام')),
            ('login', _('ورود')),
            ('password_reset', _('بازیابی رمز عبور')),
        ],
        default='signup',
        verbose_name='هدف'
    )
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    is_used = models.BooleanField(default=False, verbose_name='استفاده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    expires_at = models.DateTimeField(verbose_name='تاریخ انقضا')
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تایید')
    
    class Meta:
        verbose_name = _('کد تایید')
        verbose_name_plural = _('کدهای تایید')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'code', 'is_verified']),
            models.Index(fields=['phone_number', 'transaction_id']),
            models.Index(fields=['phone_number', 'purpose']),
        ]
    
    def __str__(self):
        return f"OTP for {self.phone_number} - {self.code}"
    
    def is_expired(self):
        """Check if OTP code has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP code is valid (not expired, not used, not verified)"""
        return not self.is_expired() and not self.is_used and not self.is_verified