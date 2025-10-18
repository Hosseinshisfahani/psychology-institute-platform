from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class WorkshopCategory(models.Model):
    """Categories for workshops"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class'))
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Workshop Category')
        verbose_name_plural = _('Workshop Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Workshop(models.Model):
    """Educational workshops with multiple sessions"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('registration_open', _('Registration Open')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('full_payment', _('Full Payment')),
        ('installment', _('Installment Payment')),
        ('both', _('Both Options')),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Slug'))
    description = models.TextField(verbose_name=_('Description'))
    short_description = models.CharField(max_length=300, verbose_name=_('Short Description'))
    category = models.ForeignKey(WorkshopCategory, on_delete=models.CASCADE, related_name='workshops', verbose_name=_('Category'))
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_workshops', verbose_name=_('Instructor'))
    
    # Status and difficulty
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('Status'))
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name=_('Difficulty'))
    
    # Scheduling
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    registration_deadline = models.DateTimeField(verbose_name=_('Registration Deadline'))
    
    # Capacity
    max_participants = models.PositiveIntegerField(default=50, verbose_name=_('Maximum Participants'))
    current_participants = models.PositiveIntegerField(default=0, verbose_name=_('Current Participants'))
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Discount Price'))
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='both', verbose_name=_('Payment Type'))
    
    # Installment options
    installment_months = models.PositiveIntegerField(default=3, verbose_name=_('Number of Installment Months'))
    
    # Workshop details
    total_hours = models.PositiveIntegerField(verbose_name=_('Total Hours'))
    language = models.CharField(max_length=10, default='fa', verbose_name=_('Language'))
    prerequisites = models.TextField(blank=True, null=True, verbose_name=_('Prerequisites'))
    learning_objectives = models.TextField(verbose_name=_('Learning Objectives'))
    
    # Media
    thumbnail = models.ImageField(upload_to='workshops/thumbnails/', blank=True, null=True, verbose_name=_('Thumbnail'))
    intro_video = models.FileField(upload_to='workshops/videos/', blank=True, null=True, verbose_name=_('Intro Video'))
    
    # Statistics
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name=_('Rating'))
    review_count = models.PositiveIntegerField(default=0, verbose_name=_('Review Count'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Published At'))
    
    class Meta:
        verbose_name = _('Workshop')
        verbose_name_plural = _('Workshops')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0
    
    @property
    def is_full(self):
        return self.current_participants >= self.max_participants
    
    @property
    def available_seats(self):
        return self.max_participants - self.current_participants
    
    @property
    def installment_amount(self):
        """Calculate monthly installment amount"""
        if self.installment_months > 0:
            return self.current_price / self.installment_months
        return self.current_price


class WorkshopSession(models.Model):
    """Individual sessions within a workshop"""
    
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='sessions', verbose_name=_('Workshop'))
    session_number = models.PositiveIntegerField(verbose_name=_('Session Number'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    
    # Scheduling
    scheduled_datetime = models.DateTimeField(verbose_name=_('Scheduled Date & Time'))
    duration_minutes = models.PositiveIntegerField(verbose_name=_('Duration (Minutes)'))
    
    # Croom integration
    meeting_link = models.URLField(blank=True, null=True, verbose_name=_('Meeting Link'))
    meeting_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Meeting ID'))
    meeting_password = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Meeting Password'))
    recording_url = models.URLField(blank=True, null=True, verbose_name=_('Recording URL'))
    
    # Session materials
    materials = models.TextField(blank=True, null=True, verbose_name=_('Session Materials'))
    homework = models.TextField(blank=True, null=True, verbose_name=_('Homework'))
    
    # Status
    is_completed = models.BooleanField(default=False, verbose_name=_('Is Completed'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Workshop Session')
        verbose_name_plural = _('Workshop Sessions')
        ordering = ['workshop', 'session_number']
        unique_together = ['workshop', 'session_number']
    
    def __str__(self):
        return f"{self.workshop.title} - Session {self.session_number}: {self.title}"


class WorkshopRegistration(models.Model):
    """User registrations for workshops"""
    
    STATUS_CHOICES = [
        ('pending_payment', _('Pending Payment')),
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('suspended', _('Suspended')),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('full_payment', _('Full Payment')),
        ('installment', _('Installment Payment')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workshop_registrations', verbose_name=_('User'))
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='registrations', verbose_name=_('Workshop'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment', verbose_name=_('Status'))
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name=_('Payment Type'))
    
    # Pricing
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Amount Paid'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount'))
    
    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Registered At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name=_('Last Accessed'))
    
    # Progress
    progress_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Progress Percentage'))
    
    class Meta:
        verbose_name = _('Workshop Registration')
        verbose_name_plural = _('Workshop Registrations')
        unique_together = ['user', 'workshop']
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.workshop.title}"
    
    def update_progress(self):
        """Calculate and update progress based on session attendance"""
        total_sessions = self.workshop.sessions.count()
        if total_sessions > 0:
            attended_sessions = self.session_attendance.filter(attended=True).count()
            self.progress_percentage = (attended_sessions / total_sessions) * 100
            self.save(update_fields=['progress_percentage'])


class WorkshopSessionAttendance(models.Model):
    """Track user attendance for workshop sessions"""
    
    registration = models.ForeignKey(WorkshopRegistration, on_delete=models.CASCADE, related_name='session_attendance', verbose_name=_('Registration'))
    session = models.ForeignKey(WorkshopSession, on_delete=models.CASCADE, related_name='attendance', verbose_name=_('Session'))
    attended = models.BooleanField(default=False, verbose_name=_('Attended'))
    attendance_marked_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Attendance Marked At'))
    
    # Time tracking
    join_time = models.DateTimeField(blank=True, null=True, verbose_name=_('Join Time'))
    leave_time = models.DateTimeField(blank=True, null=True, verbose_name=_('Leave Time'))
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name=_('Duration (Minutes)'))
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Workshop Session Attendance')
        verbose_name_plural = _('Workshop Session Attendances')
        unique_together = ['registration', 'session']
        ordering = ['session__scheduled_datetime']
    
    def __str__(self):
        return f"{self.registration.user.full_name} - {self.session.title}"


class InstallmentPlan(models.Model):
    """Installment plan for a workshop registration"""
    
    registration = models.OneToOneField(WorkshopRegistration, on_delete=models.CASCADE, related_name='installment_plan', verbose_name=_('Registration'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount'))
    number_of_installments = models.PositiveIntegerField(verbose_name=_('Number of Installments'))
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Installment Amount'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Installment Plan')
        verbose_name_plural = _('Installment Plans')
    
    def __str__(self):
        return f"Installment Plan for {self.registration}"
    
    @property
    def total_paid(self):
        """Calculate total amount paid so far"""
        return sum(payment.amount for payment in self.payments.filter(status='paid'))
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.total_paid
    
    @property
    def is_fully_paid(self):
        """Check if all installments are paid"""
        return self.payments.filter(status='paid').count() == self.number_of_installments


class InstallmentPayment(models.Model):
    """Individual installment payments"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]
    
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Plan'))
    installment_number = models.PositiveIntegerField(verbose_name=_('Installment Number'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Payment details
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Paid At'))
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Payment Method'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Transaction ID'))
    order = models.ForeignKey('payment.Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Order'))
    
    # Reminders
    reminder_sent = models.BooleanField(default=False, verbose_name=_('Reminder Sent'))
    reminder_sent_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Reminder Sent At'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Installment Payment')
        verbose_name_plural = _('Installment Payments')
        ordering = ['plan', 'installment_number']
        unique_together = ['plan', 'installment_number']
    
    def __str__(self):
        return f"Installment {self.installment_number}/{self.plan.number_of_installments} - {self.plan.registration}"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        from django.utils import timezone
        return self.status == 'pending' and self.due_date < timezone.now().date()


class WorkshopReview(models.Model):
    """Workshop reviews and ratings"""
    
    registration = models.OneToOneField(WorkshopRegistration, on_delete=models.CASCADE, related_name='review', verbose_name=_('Registration'))
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Rating'))
    title = models.CharField(max_length=200, verbose_name=_('Review Title'))
    content = models.TextField(verbose_name=_('Review Content'))
    
    # Detailed ratings
    instructor_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Instructor Rating'))
    content_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Content Rating'))
    interaction_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Interaction Rating'))
    
    is_approved = models.BooleanField(default=False, verbose_name=_('Is Approved'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Workshop Review')
        verbose_name_plural = _('Workshop Reviews')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.registration.workshop.title} by {self.registration.user.full_name}"
