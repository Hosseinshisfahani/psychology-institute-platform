from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class SessionType(models.Model):
    """Types of therapy sessions"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    duration_minutes = models.PositiveIntegerField(verbose_name=_('Duration (Minutes)'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Session Type')
        verbose_name_plural = _('Session Types')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TherapistAvailability(models.Model):
    """Therapist availability schedule"""
    
    DAYS_OF_WEEK = [
        ('monday', _('Monday')),
        ('tuesday', _('Tuesday')),
        ('wednesday', _('Wednesday')),
        ('thursday', _('Thursday')),
        ('friday', _('Friday')),
        ('saturday', _('Saturday')),
        ('sunday', _('Sunday')),
    ]
    
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability', verbose_name=_('Therapist'))
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, verbose_name=_('Day of Week'))
    start_time = models.TimeField(verbose_name=_('Start Time'))
    end_time = models.TimeField(verbose_name=_('End Time'))
    is_available = models.BooleanField(default=True, verbose_name=_('Is Available'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Therapist Availability')
        verbose_name_plural = _('Therapist Availability')
        ordering = ['day_of_week', 'start_time']
        unique_together = ['therapist', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.therapist.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Session(models.Model):
    """Therapy sessions"""
    
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('confirmed', _('Confirmed')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    ]
    
    SESSION_MODES = [
        ('online', _('Online')),
        ('in_person', _('In Person')),
        ('phone', _('Phone Call')),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_sessions', verbose_name=_('Client'))
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapist_sessions', verbose_name=_('Therapist'))
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE, related_name='sessions', verbose_name=_('Session Type'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name=_('Status'))
    mode = models.CharField(max_length=20, choices=SESSION_MODES, verbose_name=_('Mode'))
    
    # Scheduling
    scheduled_date = models.DateField(verbose_name=_('Scheduled Date'))
    scheduled_time = models.TimeField(verbose_name=_('Scheduled Time'))
    duration_minutes = models.PositiveIntegerField(verbose_name=_('Duration (Minutes)'))
    
    # Location/Meeting details
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Location'))
    meeting_link = models.URLField(blank=True, null=True, verbose_name=_('Meeting Link'))
    meeting_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Meeting ID'))
    meeting_password = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Meeting Password'))
    
    # Session details
    session_notes = models.TextField(blank=True, null=True, verbose_name=_('Session Notes'))
    goals = models.TextField(blank=True, null=True, verbose_name=_('Session Goals'))
    homework = models.TextField(blank=True, null=True, verbose_name=_('Homework'))
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    is_paid = models.BooleanField(default=False, verbose_name=_('Is Paid'))
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Payment Method'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Transaction ID'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Started At'))
    ended_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Ended At'))
    
    class Meta:
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
        ordering = ['-scheduled_date', '-scheduled_time']
    
    def __str__(self):
        return f"{self.client.full_name} with {self.therapist.full_name} - {self.scheduled_date} {self.scheduled_time}"


class SessionNote(models.Model):
    """Therapist notes for sessions"""
    
    NOTE_TYPES = [
        ('general', _('General Notes')),
        ('assessment', _('Assessment')),
        ('treatment', _('Treatment Plan')),
        ('progress', _('Progress Notes')),
        ('homework', _('Homework Assignment')),
    ]
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='notes', verbose_name=_('Session'))
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, verbose_name=_('Note Type'))
    content = models.TextField(verbose_name=_('Content'))
    is_private = models.BooleanField(default=True, verbose_name=_('Is Private'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_notes', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Session Note')
        verbose_name_plural = _('Session Notes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.session} - {self.get_note_type_display()}"


class SessionRating(models.Model):
    """Client ratings for sessions"""
    
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='rating', verbose_name=_('Session'))
    overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Overall Rating'))
    therapist_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Therapist Rating'))
    environment_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Environment Rating'))
    helpfulness_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Helpfulness Rating'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Comments'))
    would_recommend = models.BooleanField(default=True, verbose_name=_('Would Recommend'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Session Rating')
        verbose_name_plural = _('Session Ratings')
    
    def __str__(self):
        return f"Rating for {self.session} - {self.overall_rating}/5"


class SessionCancellation(models.Model):
    """Session cancellations"""
    
    CANCELLATION_REASONS = [
        ('client_request', _('Client Request')),
        ('therapist_request', _('Therapist Request')),
        ('emergency', _('Emergency')),
        ('technical_issue', _('Technical Issue')),
        ('weather', _('Weather')),
        ('other', _('Other')),
    ]
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='cancellations', verbose_name=_('Session'))
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_cancellations', verbose_name=_('Cancelled By'))
    reason = models.CharField(max_length=20, choices=CANCELLATION_REASONS, verbose_name=_('Reason'))
    explanation = models.TextField(blank=True, null=True, verbose_name=_('Explanation'))
    cancelled_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Cancelled At'))
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Refund Amount'))
    is_refunded = models.BooleanField(default=False, verbose_name=_('Is Refunded'))
    
    class Meta:
        verbose_name = _('Session Cancellation')
        verbose_name_plural = _('Session Cancellations')
        ordering = ['-cancelled_at']
    
    def __str__(self):
        return f"Cancellation for {self.session} by {self.cancelled_by.full_name}"


class SessionReminder(models.Model):
    """Session reminders"""
    
    REMINDER_TYPES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Push Notification')),
    ]
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='reminders', verbose_name=_('Session'))
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, verbose_name=_('Reminder Type'))
    scheduled_time = models.DateTimeField(verbose_name=_('Scheduled Time'))
    is_sent = models.BooleanField(default=False, verbose_name=_('Is Sent'))
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Sent At'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Session Reminder')
        verbose_name_plural = _('Session Reminders')
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"Reminder for {self.session} - {self.get_reminder_type_display()}"