from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone

User = get_user_model()


def python_weekday_to_persian(python_weekday):
    """
    Convert Python's weekday to Persian calendar weekday.
    
    Python's weekday:
        Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
    
    Persian calendar weekday (used in TherapistSchedule.DAYS_OF_WEEK):
        شنبه (Saturday)=0, یکشنبه (Sunday)=1, دوشنبه (Monday)=2, 
        سه‌شنبه (Tuesday)=3, چهارشنبه (Wednesday)=4, پنج‌شنبه (Thursday)=5, جمعه (Friday)=6
    
    Args:
        python_weekday (int): Python's datetime.weekday() result (0-6)
    
    Returns:
        int: Persian calendar day (0-6)
    """
    return (python_weekday + 2) % 7


class ClinicLocation(models.Model):
    """Central clinic locations where sessions occur"""
    
    name = models.CharField(max_length=200, verbose_name='نام کلینیک')
    address = models.TextField(verbose_name='آدرس')
    city = models.CharField(max_length=100, verbose_name='شهر')
    phone = models.CharField(max_length=20, verbose_name='تلفن')
    capacity = models.PositiveIntegerField(default=1, verbose_name='ظرفیت')
    facilities = models.JSONField(default=dict, verbose_name='امکانات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('محل کلینیک')
        verbose_name_plural = _('محل‌های کلینیک')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class AppointmentType(models.Model):
    """Define different types of therapy appointments"""
    
    name = models.CharField(max_length=100, verbose_name='نام نوع نوبت')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    default_duration_minutes = models.PositiveIntegerField(
        default=60, 
        validators=[MinValueValidator(15), MaxValueValidator(480)],
        verbose_name='مدت زمان پیش‌فرض (دقیقه)'
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='قیمت'
    )
    requires_deposit = models.BooleanField(default=True, verbose_name='نیاز به ودیعه')
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100000.00'),
        verbose_name='مبلغ ودیعه',
        help_text='در صورت نیاز به ودیعه، مبلغ آن را وارد کنید'
    )
    color = models.CharField(max_length=7, default='#007bff', verbose_name='رنگ')
    # Link appointment types to therapist specializations
    specializations = models.JSONField(
        default=list, 
        verbose_name='تخصص‌های مرتبط',
        help_text='لیست تخصص‌هایی که این نوع نوبت برای آن‌ها مناسب است'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('نوع نوبت')
        verbose_name_plural = _('انواع نوبت')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.default_duration_minutes} دقیقه)"


class TherapistSchedule(models.Model):
    """System-wide working hours and therapist availability"""
    
    DAYS_OF_WEEK = [
        (0, _('شنبه')),
        (1, _('یکشنبه')),
        (2, _('دوشنبه')),
        (3, _('سه‌شنبه')),
        (4, _('چهارشنبه')),
        (5, _('پنج‌شنبه')),
        (6, _('جمعه')),
    ]
    
    therapist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        limit_choices_to={'user_type': 'therapist'},
        verbose_name='درمانگر'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='روز هفته')
    start_time = models.TimeField(verbose_name='ساعت شروع')
    end_time = models.TimeField(verbose_name='ساعت پایان')
    location = models.ForeignKey(
        ClinicLocation, 
        on_delete=models.CASCADE,
        verbose_name='محل کار'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('برنامه درمانگر')
        verbose_name_plural = _('برنامه‌های درمانگران')
        unique_together = ['therapist', 'day_of_week', 'start_time']
        ordering = ['therapist', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.therapist.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class TherapistTimeOff(models.Model):
    """Exceptions to regular schedule (vacations, breaks)"""
    
    therapist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='time_offs',
        limit_choices_to={'user_type': 'therapist'},
        verbose_name='درمانگر'
    )
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    reason = models.CharField(max_length=200, verbose_name='دلیل')
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('مرخصی درمانگر')
        verbose_name_plural = _('مرخصی‌های درمانگران')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.therapist.full_name} - {self.start_date} تا {self.end_date}"


class Appointment(models.Model):
    """Main booking model"""
    
    STATUS_CHOICES = [
        ('pending_deposit', _('در انتظار ودیعه')),
        ('scheduled', _('رزرو شده')),
        ('confirmed', _('تأیید شده')),
        ('completed', _('تکمیل شده')),
        ('cancelled', _('لغو شده')),
        ('no_show', _('عدم حضور')),
        ('rescheduled', _('تغییر زمان')),
    ]
    
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_appointments',
        limit_choices_to={'user_type': 'client'},
        verbose_name='مراجع'
    )
    therapist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='therapist_appointments',
        limit_choices_to={'user_type': 'therapist'},
        verbose_name='درمانگر'
    )
    appointment_type = models.ForeignKey(
        AppointmentType, 
        on_delete=models.CASCADE,
        verbose_name='نوع نوبت'
    )
    location = models.ForeignKey(
        ClinicLocation, 
        on_delete=models.CASCADE,
        verbose_name='محل نوبت'
    )
    scheduled_datetime = models.DateTimeField(verbose_name='زمان نوبت')
    duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(480)],
        verbose_name='مدت زمان (دقیقه)'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='scheduled',
        verbose_name='وضعیت'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    deposit_required = models.BooleanField(default=False, verbose_name='نیاز به ودیعه')
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100000.00'),
        verbose_name='مبلغ ودیعه'
    )
    deposit_paid = models.BooleanField(default=False, verbose_name='ودیعه پرداخت شده است؟')
    deposit_paid_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ پرداخت ودیعه')
    deposit_order = models.OneToOneField(
        'payment.Order',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='appointment_deposit',
        verbose_name='سفارش ودیعه'
    )
    deposit_payment = models.OneToOneField(
        'payment.Payment',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='appointment_deposit',
        verbose_name='پرداخت ودیعه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('نوبت')
        verbose_name_plural = _('نوبت‌ها')
        ordering = ['-scheduled_datetime']
        indexes = [
            models.Index(fields=['therapist', 'scheduled_datetime']),
            models.Index(fields=['client', 'scheduled_datetime']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.client.full_name} - {self.therapist.full_name} - {self.scheduled_datetime}"
    
    @property
    def end_datetime(self):
        """Calculate appointment end time"""
        from datetime import timedelta
        return self.scheduled_datetime + timedelta(minutes=self.duration_minutes)

    def mark_deposit_paid(self, payment=None, commit=True):
        """Mark appointment deposit as paid and update status"""
        self.deposit_paid = True
        if not self.deposit_paid_at:
            self.deposit_paid_at = timezone.now()
        if payment:
            self.deposit_payment = payment
            if payment.order:
                self.deposit_order = payment.order
        if self.status == 'pending_deposit':
            self.status = 'scheduled'
        update_fields = [
            'deposit_paid',
            'deposit_paid_at',
            'deposit_payment',
            'deposit_order',
            'status',
            'updated_at'
        ]
        if commit:
            self.save(update_fields=update_fields)


class AppointmentCancellation(models.Model):
    """Track cancellations with policies"""
    
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='cancellation',
        verbose_name='نوبت'
    )
    cancelled_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='لغو شده توسط'
    )
    cancelled_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ لغو')
    reason = models.TextField(verbose_name='دلیل لغو')
    cancellation_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='هزینه لغو'
    )
    refund_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='مبلغ بازگشت'
    )
    policy_applied = models.CharField(max_length=100, blank=True, null=True, verbose_name='سیاست اعمال شده')
    
    class Meta:
        verbose_name = _('لغو نوبت')
        verbose_name_plural = _('لغوهای نوبت')
        ordering = ['-cancelled_at']
    
    def __str__(self):
        return f"لغو نوبت {self.appointment.id} - {self.cancelled_at}"


class AppointmentReschedule(models.Model):
    """Track rescheduling history"""
    
    original_appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='reschedules',
        verbose_name='نوبت اصلی'
    )
    new_appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='rescheduled_from',
        verbose_name='نوبت جدید'
    )
    rescheduled_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='تغییر زمان توسط'
    )
    rescheduled_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تغییر زمان')
    reason = models.TextField(verbose_name='دلیل تغییر زمان')
    reschedule_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='هزینه تغییر زمان'
    )
    
    class Meta:
        verbose_name = _('تغییر زمان نوبت')
        verbose_name_plural = _('تغییر زمان‌های نوبت')
        ordering = ['-rescheduled_at']
    
    def __str__(self):
        return f"تغییر زمان نوبت {self.original_appointment.id} به {self.new_appointment.id}"


class CancellationPolicy(models.Model):
    """Define cancellation rules"""
    
    name = models.CharField(max_length=100, verbose_name='نام سیاست')
    hours_before_appointment = models.PositiveIntegerField(
        verbose_name='ساعت قبل از نوبت',
        help_text='حداقل ساعت قبل از نوبت که این سیاست اعمال می‌شود'
    )
    cancellation_fee_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='درصد هزینه لغو'
    )
    description = models.TextField(verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('سیاست لغو')
        verbose_name_plural = _('سیاست‌های لغو')
        ordering = ['-hours_before_appointment']
    
    def __str__(self):
        return f"{self.name} - {self.hours_before_appointment} ساعت قبل"


class AppointmentReminder(models.Model):
    """Automated reminders"""
    
    REMINDER_TYPES = [
        ('email', _('ایمیل')),
        ('sms', _('پیامک')),
        ('push', _('اعلان')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('در انتظار')),
        ('sent', _('ارسال شده')),
        ('failed', _('ناموفق')),
    ]
    
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='reminders',
        verbose_name='نوبت'
    )
    reminder_type = models.CharField(
        max_length=10, 
        choices=REMINDER_TYPES,
        verbose_name='نوع یادآوری'
    )
    scheduled_time = models.DateTimeField(verbose_name='زمان ارسال')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان ارسال واقعی')
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='وضعیت'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('یادآوری نوبت')
        verbose_name_plural = _('یادآوری‌های نوبت')
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"یادآوری {self.get_reminder_type_display()} برای نوبت {self.appointment.id}"
