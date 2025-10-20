from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


class Staff(models.Model):
    """Staff members who can handle appointments"""
    
    ROLE_CHOICES = [
        ('consultant', _('مشاور')),
        ('psychologist', _('روانشناس')),
        ('counselor', _('راهنما')),
        ('receptionist', _('پذیرش')),
        ('coordinator', _('هماهنگ کننده')),
        ('other', _('سایر')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', verbose_name='کاربر')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name='نقش')
    title = models.CharField(max_length=100, blank=True, verbose_name='عنوان')
    bio = models.TextField(blank=True, null=True, verbose_name='بیوگرافی')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    can_accept_appointments = models.BooleanField(default=True, verbose_name='می‌تواند قرار ملاقات بپذیرد')
    office_location = models.CharField(max_length=100, blank=True, verbose_name='محل دفتر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('کارمند')
        verbose_name_plural = _('کارمندان')
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    def get_full_name(self):
        return self.user.get_full_name()


class Room(models.Model):
    """Meeting rooms at the institute"""
    
    name = models.CharField(max_length=100, verbose_name='نام اتاق')
    building = models.CharField(max_length=100, blank=True, verbose_name='ساختمان')
    floor = models.CharField(max_length=20, blank=True, verbose_name='طبقه')
    capacity = models.PositiveIntegerField(default=2, verbose_name='ظرفیت')
    facilities = models.TextField(blank=True, null=True, verbose_name='امکانات')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('اتاق')
        verbose_name_plural = _('اتاق‌ها')
        ordering = ['building', 'floor', 'name']
    
    def __str__(self):
        location = []
        if self.building:
            location.append(self.building)
        if self.floor:
            location.append(f"طبقه {self.floor}")
        location.append(self.name)
        return " - ".join(location)


class AppointmentType(models.Model):
    """Types of appointments available"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')
    requires_approval = models.BooleanField(default=True, verbose_name='نیاز به تأیید دارد')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('نوع قرار ملاقات')
        verbose_name_plural = _('انواع قرارهای ملاقات')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    """Available time slots for appointments"""
    
    DAYS_OF_WEEK = [
        (0, _('شنبه')),
        (1, _('یکشنبه')),
        (2, _('دوشنبه')),
        (3, _('سه‌شنبه')),
        (4, _('چهارشنبه')),
        (5, _('پنج‌شنبه')),
        (6, _('جمعه')),
    ]
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='time_slots', verbose_name='کارمند', blank=True, null=True)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='روز هفته')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    max_appointments = models.PositiveIntegerField(default=1, verbose_name='حداکثر تعداد قرار ملاقات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('بازه زمانی')
        verbose_name_plural = _('بازه‌های زمانی')
        ordering = ['day_of_week', 'start_time']
        unique_together = ['staff', 'day_of_week', 'start_time', 'end_time']
    
    def __str__(self):
        staff_name = self.staff.get_full_name() if self.staff else "عمومی"
        return f"{staff_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    """In-person appointments at the institute"""
    
    STATUS_CHOICES = [
        ('pending', _('در انتظار تأیید')),
        ('confirmed', _('تأیید شده')),
        ('completed', _('انجام شده')),
        ('cancelled', _('لغو شده')),
        ('no_show', _('عدم حضور')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', verbose_name='کاربر')
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE, related_name='appointments', verbose_name='نوع قرار ملاقات')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name='کارمند')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name='اتاق')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # Scheduling
    appointment_date = models.DateField(verbose_name='تاریخ قرار ملاقات')
    appointment_time = models.TimeField(verbose_name='زمان قرار ملاقات')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')
    
    # Details
    purpose = models.TextField(verbose_name='هدف ملاقات')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    internal_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های داخلی')
    
    # Confirmation
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_appointments', verbose_name='تأیید شده توسط')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='تأیید شده در')
    confirmation_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های تأیید')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='انجام شده در')
    
    class Meta:
        verbose_name = _('قرار ملاقات')
        verbose_name_plural = _('قرارهای ملاقات')
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['staff', 'appointment_date', 'appointment_time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.appointment_type.name} - {self.appointment_date} {self.appointment_time}"
    
    @property
    def end_time(self):
        """Calculate end time based on start time and duration"""
        start_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
        return end_datetime.time()
    
    def confirm(self, confirmed_by, notes='', staff=None, room=None):
        """Confirm the appointment"""
        self.status = 'confirmed'
        self.confirmed_by = confirmed_by
        self.confirmed_at = timezone.now()
        self.confirmation_notes = notes
        if staff:
            self.staff = staff
        if room:
            self.room = room
        self.save()
        
        # TODO: Send confirmation notification to user
        return self
    
    def cancel(self, cancelled_by, reason=''):
        """Cancel the appointment"""
        self.status = 'cancelled'
        self.save()
        
        # Create cancellation record
        AppointmentCancellation.objects.create(
            appointment=self,
            cancelled_by=cancelled_by,
            reason=reason
        )
        
        # TODO: Send cancellation notification
        return self
    
    def complete(self):
        """Mark appointment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        return self


class AppointmentCancellation(models.Model):
    """Appointment cancellation records"""
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='cancellations', verbose_name='قرار ملاقات')
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointment_cancellations', verbose_name='لغو شده توسط')
    reason = models.TextField(verbose_name='دلیل لغو')
    cancelled_at = models.DateTimeField(auto_now_add=True, verbose_name='لغو شده در')
    
    class Meta:
        verbose_name = _('لغو قرار ملاقات')
        verbose_name_plural = _('لغوهای قرار ملاقات')
        ordering = ['-cancelled_at']
    
    def __str__(self):
        return f"لغو {self.appointment} توسط {self.cancelled_by.get_full_name()}"


class AppointmentReminder(models.Model):
    """Appointment reminders"""
    
    REMINDER_TYPES = [
        ('email', _('ایمیل')),
        ('sms', _('پیامک')),
        ('notification', _('اعلان')),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders', verbose_name='قرار ملاقات')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, verbose_name='نوع یادآوری')
    scheduled_time = models.DateTimeField(verbose_name='زمان برنامه‌ریزی شده')
    is_sent = models.BooleanField(default=False, verbose_name='ارسال شده')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='ارسال شده در')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('یادآوری قرار ملاقات')
        verbose_name_plural = _('یادآوری‌های قرار ملاقات')
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"یادآوری {self.get_reminder_type_display()} برای {self.appointment}"


class AppointmentFeedback(models.Model):
    """User feedback for appointments"""
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='feedback', verbose_name='قرار ملاقات')
    overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز کلی')
    staff_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True, verbose_name='امتیاز کارمند')
    location_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True, verbose_name='امتیاز مکان')
    comments = models.TextField(blank=True, null=True, verbose_name='نظرات')
    would_recommend = models.BooleanField(default=True, verbose_name='توصیه می‌کند')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('بازخورد قرار ملاقات')
        verbose_name_plural = _('بازخوردهای قرار ملاقات')
    
    def __str__(self):
        return f"بازخورد برای {self.appointment} - {self.overall_rating}/5"