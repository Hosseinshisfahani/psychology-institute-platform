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
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_cohorts', verbose_name=_('Instructor'))
    
    # Scheduling
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    class_time = models.TimeField(verbose_name=_('Class Time'))
    duration_minutes = models.PositiveIntegerField(verbose_name=_('Duration (Minutes)'))
    total_sessions = models.PositiveIntegerField(verbose_name=_('Total Sessions'))
    
    # Pricing
    full_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Full Price'))
    installment_3_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('3 Installments Price'))
    installment_6_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('6 Installments Price'))
    
    # Capacity
    max_students = models.PositiveIntegerField(verbose_name=_('Maximum Students'))
    current_enrollments = models.PositiveIntegerField(default=0, verbose_name=_('Current Enrollments'))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name=_('Status'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cohort')
        verbose_name_plural = _('Cohorts')
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
    
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='sessions', verbose_name=_('Cohort'))
    session_number = models.PositiveIntegerField(verbose_name=_('Session Number'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    
    # Scheduling
    scheduled_date = models.DateField(verbose_name=_('Scheduled Date'))
    scheduled_time = models.TimeField(verbose_name=_('Scheduled Time'))
    duration_minutes = models.PositiveIntegerField(verbose_name=_('Duration (Minutes)'))
    
    # Session details
    is_completed = models.BooleanField(default=False, verbose_name=_('Is Completed'))
    actual_start_time = models.DateTimeField(blank=True, null=True, verbose_name=_('Actual Start Time'))
    actual_end_time = models.DateTimeField(blank=True, null=True, verbose_name=_('Actual End Time'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Session Notes'))
    
    # Recording
    recording_file = models.FileField(upload_to='cohorts/recordings/', blank=True, null=True, verbose_name=_('Recording File'))
    recording_url = models.URLField(blank=True, null=True, verbose_name=_('Recording URL'))
    is_recording_available = models.BooleanField(default=False, verbose_name=_('Is Recording Available'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cohort Session')
        verbose_name_plural = _('Cohort Sessions')
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
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cohort_enrollments', verbose_name=_('Student'))
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='enrollments', verbose_name=_('Cohort'))
    
    # Enrollment details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    payment_type = models.CharField(max_length=20, choices=Cohort.PAYMENT_TYPES, verbose_name=_('Payment Type'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name=_('Payment Status'))
    
    # Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Amount Paid'))
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Remaining Amount'))
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Enrolled At'))
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Confirmed At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    
    class Meta:
        verbose_name = _('Cohort Enrollment')
        verbose_name_plural = _('Cohort Enrollments')
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
    
    enrollment = models.ForeignKey(CohortEnrollment, on_delete=models.CASCADE, related_name='installments', verbose_name=_('Enrollment'))
    installment_number = models.PositiveIntegerField(verbose_name=_('Installment Number'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Payment details
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Paid At'))
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Payment Method'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Transaction ID'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cohort Installment')
        verbose_name_plural = _('Cohort Installments')
        ordering = ['installment_number']
        unique_together = ['enrollment', 'installment_number']
    
    def __str__(self):
        return f"{self.enrollment.student.full_name} - Installment {self.installment_number}"
    
    @property
    def is_overdue(self):
        return self.status == 'due' and timezone.now().date() > self.due_date


class CohortAttendance(models.Model):
    """Student attendance for cohort sessions"""
    
    enrollment = models.ForeignKey(CohortEnrollment, on_delete=models.CASCADE, related_name='attendance', verbose_name=_('Enrollment'))
    session = models.ForeignKey(CohortSession, on_delete=models.CASCADE, related_name='attendance', verbose_name=_('Session'))
    
    # Attendance details
    is_present = models.BooleanField(default=False, verbose_name=_('Is Present'))
    arrived_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Arrived At'))
    left_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Left At'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cohort Attendance')
        verbose_name_plural = _('Cohort Attendance')
        unique_together = ['enrollment', 'session']
    
    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.session.title}"
