from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


class Staff(models.Model):
    """Staff members who provide in-person appointments at the institute"""
    
    ROLE_CHOICES = [
        ('counselor', _('مشاور')),
        ('psychologist', _('روانشناس')),
        ('psychiatrist', _('روانپزشک')),
        ('registrar', _('کارشناس پذیرش')),
        ('director', _('مدیر')),
        ('other', _('سایر')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', verbose_name='کاربر')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name='نقش')
    title = models.CharField(max_length=200, blank=True, verbose_name='عنوان شغلی')
    bio = models.TextField(blank=True, null=True, verbose_name='بیوگرافی')
    specializations = models.TextField(blank=True, null=True, verbose_name='تخصص‌ها', help_text='تخصص‌ها را با کاما جدا کنید')
    room_number = models.CharField(max_length=50, blank=True, verbose_name='شماره اتاق')
    phone_extension = models.CharField(max_length=20, blank=True, verbose_name='داخلی تلفن')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    accepts_appointments = models.BooleanField(default=True, verbose_name='پذیرش وقت ملاقات')
    profile_image = models.ImageField(upload_to='staff_profiles/', blank=True, null=True, verbose_name='تصویر پروفایل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('کارمند')
        verbose_name_plural = _('کارمندان')
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    def get_full_name(self):
        return self.user.get_full_name()


class AppointmentRoom(models.Model):
    """Physical rooms at the institute for appointments"""
    
    name = models.CharField(max_length=100, verbose_name='نام اتاق')
    room_number = models.CharField(max_length=20, unique=True, verbose_name='شماره اتاق')
    floor = models.IntegerField(verbose_name='طبقه')
    capacity = models.PositiveIntegerField(default=2, verbose_name='ظرفیت')
    facilities = models.TextField(blank=True, verbose_name='امکانات', help_text='امکانات موجود در اتاق')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    notes = models.TextField(blank=True, verbose_name='یادداشت‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('اتاق ملاقات')
        verbose_name_plural = _('اتاق‌های ملاقات')
        ordering = ['floor', 'room_number']
    
    def __str__(self):
        return f"{self.name} - اتاق {self.room_number} (طبقه {self.floor})"


class AppointmentType(models.Model):
    """Types of in-person appointments"""
    
    name = models.CharField(max_length=100, verbose_name='نام نوع ملاقات')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='هزینه')
    requires_preparation = models.BooleanField(default=False, verbose_name='نیاز به آمادگی قبلی')
    preparation_instructions = models.TextField(blank=True, null=True, verbose_name='دستورالعمل آمادگی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    max_advance_booking_days = models.PositiveIntegerField(default=30, verbose_name='حداکثر روز رزرو از قبل')
    min_advance_booking_hours = models.PositiveIntegerField(default=24, verbose_name='حداقل ساعت رزرو از قبل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('نوع ملاقات')
        verbose_name_plural = _('انواع ملاقات')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.duration_minutes} دقیقه)"


class StaffAvailability(models.Model):
    """Staff availability schedule for in-person appointments"""
    
    DAYS_OF_WEEK = [
        (0, _('شنبه')),
        (1, _('یکشنبه')),
        (2, _('دوشنبه')),
        (3, _('سه‌شنبه')),
        (4, _('چهارشنبه')),
        (5, _('پنج‌شنبه')),
        (6, _('جمعه')),
    ]
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='availability', verbose_name='کارمند')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='روز هفته')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    appointment_types = models.ManyToManyField(AppointmentType, verbose_name='انواع ملاقات قابل ارائه')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('برنامه حضور کارمند')
        verbose_name_plural = _('برنامه‌های حضور کارمندان')
        ordering = ['staff', 'day_of_week', 'start_time']
        unique_together = ['staff', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class TimeSlot(models.Model):
    """Available time slots for appointments"""
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='time_slots', verbose_name='کارمند')
    date = models.DateField(verbose_name='تاریخ')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    is_booked = models.BooleanField(default=False, verbose_name='رزرو شده')
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE, related_name='time_slots', verbose_name='نوع ملاقات', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('بازه زمانی')
        verbose_name_plural = _('بازه‌های زمانی')
        ordering = ['date', 'start_time']
        unique_together = ['staff', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date} {self.start_time}-{self.end_time}"
    
    @property
    def is_past(self):
        """Check if the time slot is in the past"""
        slot_datetime = datetime.combine(self.date, self.start_time)
        return timezone.make_aware(slot_datetime) < timezone.now()


class Appointment(models.Model):
    """In-person appointments at the institute"""
    
    STATUS_CHOICES = [
        ('pending', _('در انتظار تایید')),
        ('confirmed', _('تایید شده')),
        ('completed', _('انجام شده')),
        ('cancelled', _('لغو شده')),
        ('no_show', _('عدم حضور')),
    ]
    
    # Basic information
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', verbose_name='مراجع')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments', verbose_name='کارمند')
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE, related_name='appointments', verbose_name='نوع ملاقات')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # Scheduling
    date = models.DateField(verbose_name='تاریخ')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment', verbose_name='بازه زمانی')
    
    # Location details
    room = models.ForeignKey(AppointmentRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name='اتاق')
    
    # Appointment details
    purpose = models.TextField(verbose_name='هدف ملاقات')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    internal_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های داخلی', help_text='فقط قابل مشاهده توسط کارمندان')
    
    # Contact information
    phone_number = models.CharField(max_length=20, verbose_name='شماره تماس')
    alternative_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='شماره تماس جایگزین')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='هزینه')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    
    # Confirmation details
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='تایید شده در')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='confirmed_appointments', verbose_name='تایید شده توسط')
    
    # Completion details
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='انجام شده در')
    arrival_time = models.TimeField(blank=True, null=True, verbose_name='زمان حضور')
    departure_time = models.TimeField(blank=True, null=True, verbose_name='زمان خروج')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('وقت ملاقات')
        verbose_name_plural = _('وقت‌های ملاقات')
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.client.get_full_name()} با {self.staff.get_full_name()} - {self.date} {self.start_time}"
    
    @property
    def is_past(self):
        """Check if the appointment is in the past"""
        appointment_datetime = datetime.combine(self.date, self.start_time)
        return timezone.make_aware(appointment_datetime) < timezone.now()
    
    def confirm(self, user):
        """Confirm the appointment"""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.confirmed_by = user
        if self.time_slot:
            self.time_slot.is_booked = True
            self.time_slot.save()
        self.save()
    
    def complete(self):
        """Mark appointment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel(self, reason=''):
        """Cancel the appointment"""
        self.status = 'cancelled'
        if self.time_slot:
            self.time_slot.is_booked = False
            self.time_slot.save()
        self.save()
        
        # Create cancellation record
        if reason:
            AppointmentCancellation.objects.create(
                appointment=self,
                cancelled_by=self.client,
                reason='client_request',
                explanation=reason
            )


class AppointmentCancellation(models.Model):
    """Appointment cancellations tracking"""
    
    CANCELLATION_REASONS = [
        ('client_request', _('درخواست مراجع')),
        ('staff_request', _('درخواست کارمند')),
        ('emergency', _('اضطراری')),
        ('institute_closed', _('تعطیلی موسسه')),
        ('other', _('سایر')),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='cancellations', verbose_name='وقت ملاقات')
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointment_cancellations', verbose_name='لغو شده توسط')
    reason = models.CharField(max_length=20, choices=CANCELLATION_REASONS, verbose_name='دلیل')
    explanation = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    cancelled_at = models.DateTimeField(auto_now_add=True, verbose_name='لغو شده در')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ بازگشت')
    is_refunded = models.BooleanField(default=False, verbose_name='بازگشت داده شده')
    
    class Meta:
        verbose_name = _('لغو ملاقات')
        verbose_name_plural = _('لغوهای ملاقات')
        ordering = ['-cancelled_at']
    
    def __str__(self):
        return f"لغو {self.appointment} توسط {self.cancelled_by.get_full_name()}"


class AppointmentReminder(models.Model):
    """Appointment reminders"""
    
    REMINDER_TYPES = [
        ('sms', _('پیامک')),
        ('email', _('ایمیل')),
        ('call', _('تماس تلفنی')),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders', verbose_name='وقت ملاقات')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, verbose_name='نوع یادآوری')
    scheduled_time = models.DateTimeField(verbose_name='زمان برنامه‌ریزی شده')
    is_sent = models.BooleanField(default=False, verbose_name='ارسال شده')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='ارسال شده در')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('یادآوری ملاقات')
        verbose_name_plural = _('یادآوری‌های ملاقات')
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"یادآوری برای {self.appointment} - {self.get_reminder_type_display()}"


class AppointmentFeedback(models.Model):
    """Client feedback for appointments"""
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='feedback', verbose_name='وقت ملاقات')
    overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز کلی')
    staff_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز کارمند')
    facility_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز محیط')
    waiting_time_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز زمان انتظار')
    comments = models.TextField(blank=True, null=True, verbose_name='نظرات')
    would_recommend = models.BooleanField(default=True, verbose_name='توصیه می‌کند')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('بازخورد ملاقات')
        verbose_name_plural = _('بازخوردهای ملاقات')
    
    def __str__(self):
        return f"بازخورد برای {self.appointment} - {self.overall_rating}/5"