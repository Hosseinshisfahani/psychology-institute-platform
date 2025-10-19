from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Cohort(models.Model):
    """Scheduled class cohorts for the institution"""
    
    STATUS_CHOICES = [
        ('upcoming', _('Upcoming')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    PAYMENT_TYPES = [
        ('full', _('Full Payment')),
        ('installment_3', _('3 Installments')),
        ('installment_6', _('6 Installments')),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_cohorts', verbose_name='مربی')
    
    # Scheduling
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    class_time = models.TimeField(verbose_name='زمان کلاس')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت دقیقه')
    total_sessions = models.PositiveIntegerField(verbose_name='تعداد کل جلسات')
    
    # Pricing
    full_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت کامل')
    installment_3_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='قیمت 3 قسط')
    installment_6_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='قیمت 6 قسط')
    
    # Capacity
    max_students = models.PositiveIntegerField(verbose_name='حداکثر دانش‌آموزان')
    current_enrollments = models.PositiveIntegerField(default=0, verbose_name='ثبت‌نام‌های فعلی')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='وضعیت')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('گروه')
        verbose_name_plural = _('گروه‌ها')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
    
    @property
    def is_full(self):
        return self.current_enrollments >= self.max_students
    
    @property
    def available_spots(self):
        return self.max_students - self.current_enrollments


class CohortSession(models.Model):
    """Individual sessions within a cohort"""
    
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='sessions', verbose_name='گروه')
    session_number = models.PositiveIntegerField(verbose_name='شماره جلسه')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    
    # Scheduling
    scheduled_date = models.DateField(verbose_name='تاریخ برنامه‌ریزی شده')
    scheduled_time = models.TimeField(verbose_name='زمان برنامه‌ریزی شده')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت دقیقه')
    
    # Session details
    is_completed = models.BooleanField(default=False, verbose_name='تکمیل شده')
    actual_start_time = models.DateTimeField(blank=True, null=True, verbose_name='زمان شروع واقعی')
    actual_end_time = models.DateTimeField(blank=True, null=True, verbose_name='زمان پایان واقعی')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های جلسه')
    
    # Recording
    recording_file = models.FileField(upload_to='cohorts/recordings/', blank=True, null=True, verbose_name='فایل ضبط')
    recording_url = models.URLField(blank=True, null=True, verbose_name='لینک ضبط')
    is_recording_available = models.BooleanField(default=False, verbose_name='ضبط در دسترس')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('جلسه گروه')
        verbose_name_plural = _('جلسات گروه')
        ordering = ['session_number']
        unique_together = ['cohort', 'session_number']
    
    def __str__(self):
        return f"{self.cohort.title} - Session {self.session_number}"


class CohortEnrollment(models.Model):
    """Student enrollments in cohorts"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('dropped', _('Dropped')),
        ('suspended', _('Suspended')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('partial', _('Partial')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('refunded', _('Refunded')),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cohort_enrollments', verbose_name='دانش‌آموز')
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='enrollments', verbose_name='گروه')
    
    # Enrollment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    payment_type = models.CharField(max_length=20, choices=Cohort.PAYMENT_TYPES, verbose_name='نوع پرداخت')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='وضعیت پرداخت')
    
    # Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ کل')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ پرداخت شده')
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ باقی‌مانده')
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت‌نام')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تأیید')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    
    class Meta:
        verbose_name = _('ثبت‌نام گروه')
        verbose_name_plural = _('ثبت‌نام‌های گروه')
        unique_together = ['student', 'cohort']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.cohort.title}"
    
    def save(self, *args, **kwargs):
        self.remaining_amount = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)


class CohortInstallment(models.Model):
    """Installment payments for cohort enrollments"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('due', _('Due')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]
    
    enrollment = models.ForeignKey(CohortEnrollment, on_delete=models.CASCADE, related_name='installments', verbose_name='ثبت‌نام')
    installment_number = models.PositiveIntegerField(verbose_name='شماره قسط')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ')
    due_date = models.DateField(verbose_name='تاریخ سررسید')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # Payment details
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ پرداخت')
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('قسط گروه')
        verbose_name_plural = _('قسط‌های گروه')
        ordering = ['installment_number']
        unique_together = ['enrollment', 'installment_number']
    
    def __str__(self):
        return f"{self.enrollment.student.full_name} - Installment {self.installment_number}"
    
    @property
    def is_overdue(self):
        return self.status == 'due' and timezone.now().date() > self.due_date


class CohortAttendance(models.Model):
    """Student attendance for cohort sessions"""
    
    enrollment = models.ForeignKey(CohortEnrollment, on_delete=models.CASCADE, related_name='attendance', verbose_name='ثبت‌نام')
    session = models.ForeignKey(CohortSession, on_delete=models.CASCADE, related_name='attendance', verbose_name='جلسه')
    
    # Attendance details
    is_present = models.BooleanField(default=False, verbose_name='حاضر')
    arrived_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان ورود')
    left_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان خروج')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('حضور گروه')
        verbose_name_plural = _('حضورهای گروه')
        unique_together = ['enrollment', 'session']
    
    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.session.title}"
