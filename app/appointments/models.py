from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class AppointmentType(models.Model):
    """Types of appointments available at the institute"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    duration_minutes = models.PositiveIntegerField(
        verbose_name=_('Duration (Minutes)'),
        validators=[MinValueValidator(15), MaxValueValidator(240)]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Price'),
        validators=[MinValueValidator(0)]
    )
    requires_specialist = models.BooleanField(
        default=False, 
        verbose_name=_('Requires Specialist')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Appointment Type')
        verbose_name_plural = _('Appointment Types')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Specialist(models.Model):
    """Specialists working at the institute"""
    
    SPECIALIZATION_CHOICES = [
        ('clinical_psychology', _('Clinical Psychology')),
        ('counseling', _('Counseling')),
        ('child_psychology', _('Child Psychology')),
        ('family_therapy', _('Family Therapy')),
        ('neuropsychology', _('Neuropsychology')),
        ('educational_psychology', _('Educational Psychology')),
        ('other', _('Other')),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='specialist_profile',
        verbose_name=_('User')
    )
    specialization = models.CharField(
        max_length=50, 
        choices=SPECIALIZATION_CHOICES,
        verbose_name=_('Specialization')
    )
    bio = models.TextField(blank=True, null=True, verbose_name=_('Biography'))
    education = models.TextField(blank=True, null=True, verbose_name=_('Education'))
    certifications = models.TextField(blank=True, null=True, verbose_name=_('Certifications'))
    experience_years = models.PositiveIntegerField(
        default=0, 
        verbose_name=_('Years of Experience')
    )
    room_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_('Room Number')
    )
    is_available = models.BooleanField(default=True, verbose_name=_('Is Available'))
    profile_image = models.ImageField(
        upload_to='specialists/', 
        blank=True, 
        null=True,
        verbose_name=_('Profile Image')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Specialist')
        verbose_name_plural = _('Specialists')
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"


class TimeSlot(models.Model):
    """Available time slots for appointments at the institute"""
    
    DAYS_OF_WEEK = [
        (0, _('Saturday')),
        (1, _('Sunday')),
        (2, _('Monday')),
        (3, _('Tuesday')),
        (4, _('Wednesday')),
        (5, _('Thursday')),
        (6, _('Friday')),
    ]
    
    specialist = models.ForeignKey(
        Specialist, 
        on_delete=models.CASCADE, 
        related_name='time_slots',
        verbose_name=_('Specialist'),
        blank=True,
        null=True
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name=_('Day of Week'))
    start_time = models.TimeField(verbose_name=_('Start Time'))
    end_time = models.TimeField(verbose_name=_('End Time'))
    is_available = models.BooleanField(default=True, verbose_name=_('Is Available'))
    max_appointments = models.PositiveIntegerField(
        default=1, 
        verbose_name=_('Maximum Appointments'),
        help_text=_('Maximum number of appointments for this time slot')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Time Slot')
        verbose_name_plural = _('Time Slots')
        ordering = ['day_of_week', 'start_time']
        unique_together = [['specialist', 'day_of_week', 'start_time', 'end_time']]
    
    def __str__(self):
        specialist_name = self.specialist.user.get_full_name() if self.specialist else "General"
        return f"{specialist_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    """In-person appointments at the institute"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    ]
    
    # Unique identifier
    appointment_number = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        verbose_name=_('Appointment Number')
    )
    
    # Appointment details
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='appointments',
        verbose_name=_('Client')
    )
    appointment_type = models.ForeignKey(
        AppointmentType, 
        on_delete=models.CASCADE,
        verbose_name=_('Appointment Type')
    )
    specialist = models.ForeignKey(
        Specialist, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='appointments',
        verbose_name=_('Specialist')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    
    # Scheduling
    appointment_date = models.DateField(verbose_name=_('Appointment Date'))
    appointment_time = models.TimeField(verbose_name=_('Appointment Time'))
    duration_minutes = models.PositiveIntegerField(verbose_name=_('Duration (Minutes)'))
    
    # Location details
    room_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_('Room Number')
    )
    
    # Contact information
    client_phone = models.CharField(
        max_length=20, 
        verbose_name=_('Client Phone'),
        help_text=_('Contact number for appointment reminders')
    )
    emergency_contact = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_('Emergency Contact')
    )
    
    # Additional information
    reason_for_visit = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Reason for Visit')
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    
    # Payment
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Price')
    )
    is_paid = models.BooleanField(default=False, verbose_name=_('Is Paid'))
    payment_method = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name=_('Payment Method')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['specialist']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.appointment_number:
            # Generate unique appointment number
            self.appointment_number = self.generate_appointment_number()
        super().save(*args, **kwargs)
    
    def generate_appointment_number(self):
        """Generate a unique appointment number"""
        date_str = timezone.now().strftime('%Y%m%d')
        random_str = str(uuid.uuid4())[:4].upper()
        return f"APT-{date_str}-{random_str}"
    
    def __str__(self):
        return f"{self.appointment_number} - {self.client.get_full_name()} - {self.appointment_date}"


class AppointmentReminder(models.Model):
    """Reminders for appointments"""
    
    REMINDER_TYPES = [
        ('sms', _('SMS')),
        ('email', _('Email')),
        ('call', _('Phone Call')),
    ]
    
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='reminders',
        verbose_name=_('Appointment')
    )
    reminder_type = models.CharField(
        max_length=20, 
        choices=REMINDER_TYPES,
        verbose_name=_('Reminder Type')
    )
    scheduled_time = models.DateTimeField(verbose_name=_('Scheduled Time'))
    is_sent = models.BooleanField(default=False, verbose_name=_('Is Sent'))
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Sent At'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Appointment Reminder')
        verbose_name_plural = _('Appointment Reminders')
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"Reminder for {self.appointment.appointment_number} - {self.get_reminder_type_display()}"


class WaitingList(models.Model):
    """Waiting list for appointments"""
    
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='waiting_list_entries',
        verbose_name=_('Client')
    )
    appointment_type = models.ForeignKey(
        AppointmentType, 
        on_delete=models.CASCADE,
        verbose_name=_('Appointment Type')
    )
    specialist = models.ForeignKey(
        Specialist, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Preferred Specialist')
    )
    preferred_days = models.JSONField(
        default=list, 
        verbose_name=_('Preferred Days'),
        help_text=_('List of preferred days of the week')
    )
    preferred_time_start = models.TimeField(
        blank=True, 
        null=True,
        verbose_name=_('Preferred Time Start')
    )
    preferred_time_end = models.TimeField(
        blank=True, 
        null=True,
        verbose_name=_('Preferred Time End')
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Waiting List Entry')
        verbose_name_plural = _('Waiting List Entries')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.appointment_type.name}"