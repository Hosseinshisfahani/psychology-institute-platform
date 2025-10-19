from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Therapist(models.Model):
    """Therapist profile extending User model"""
    
    SPECIALIZATION_CHOICES = [
        ('individual', _('Individual Therapy')),
        ('couple', _('Couple Therapy')),
        ('family', _('Family Therapy')),
        ('group', _('Group Therapy')),
        ('child', _('Child Therapy')),
        ('adolescent', _('Adolescent Therapy')),
        ('addiction', _('Addiction Therapy')),
        ('trauma', _('Trauma Therapy')),
        ('anxiety', _('Anxiety Therapy')),
        ('depression', _('Depression Therapy')),
        ('other', _('Other')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile', verbose_name='کاربر')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, verbose_name='تخصص')
    bio = models.TextField(blank=True, null=True, verbose_name='بیوگرافی')
    education = models.TextField(blank=True, null=True, verbose_name='تحصیلات')
    certifications = models.TextField(blank=True, null=True, verbose_name='گواهینامه‌ها')
    experience_start_date = models.DateField(blank=True, null=True, verbose_name='تاریخ شروع تجربه')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='نرخ ساعتی')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    profile_image = models.ImageField(upload_to='therapist_profiles/', blank=True, null=True, verbose_name='تصویر پروفایل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('درمانگر')
        verbose_name_plural = _('درمانگران')
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_specialization_display()}"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_specialization_display(self):
        return dict(self.SPECIALIZATION_CHOICES).get(self.specialization, self.specialization)


class SessionType(models.Model):
    """Types of therapy sessions"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت دقیقه')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('نوع نوبت')
        verbose_name_plural = _('انواع نوبت')
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
    
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='availability', verbose_name='درمانگر')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, verbose_name='روز هفته')
    start_time = models.TimeField(verbose_name='زمان شروع')
    end_time = models.TimeField(verbose_name='زمان پایان')
    is_available = models.BooleanField(default=True, verbose_name='در دسترس')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('دسترسی درمانگر')
        verbose_name_plural = _('دسترسی‌های درمانگر')
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
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_sessions', verbose_name='مراجع')
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='therapist_sessions', verbose_name='درمانگر')
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE, related_name='sessions', verbose_name='نوع نوبت')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name='وضعیت')
    mode = models.CharField(max_length=20, choices=SESSION_MODES, verbose_name='حالت')
    
    # Scheduling
    scheduled_date = models.DateField(verbose_name='تاریخ برنامه‌ریزی شده')
    scheduled_time = models.TimeField(verbose_name='زمان برنامه‌ریزی شده')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت دقیقه')
    
    # Location/Meeting details
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='مکان')
    meeting_link = models.URLField(blank=True, null=True, verbose_name='لینک جلسه')
    meeting_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه جلسه')
    meeting_password = models.CharField(max_length=50, blank=True, null=True, verbose_name='رمز عبور جلسه')
    
    # Session details
    session_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های جلسه')
    goals = models.TextField(blank=True, null=True, verbose_name='اهداف جلسه')
    homework = models.TextField(blank=True, null=True, verbose_name='تکلیف')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='شروع شده در')
    ended_at = models.DateTimeField(blank=True, null=True, verbose_name='پایان یافته در')
    
    class Meta:
        verbose_name = _('نوبت')
        verbose_name_plural = _('نوبت‌ها')
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
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='notes', verbose_name='نوبت')
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, verbose_name='نوع یادداشت')
    content = models.TextField(verbose_name='محتوای')
    is_private = models.BooleanField(default=True, verbose_name='خصوصی')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_notes', verbose_name='ایجاد شده توسط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('یادداشت نوبت')
        verbose_name_plural = _('یادداشت‌های نوبت')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.session} - {self.get_note_type_display()}"


class SessionRating(models.Model):
    """Client ratings for sessions"""
    
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='rating', verbose_name='نوبت')
    overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز کلی')
    therapist_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز درمانگر')
    environment_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز محیط')
    helpfulness_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز مفید بودن')
    comments = models.TextField(blank=True, null=True, verbose_name='نظرات')
    would_recommend = models.BooleanField(default=True, verbose_name='توصیه می‌کند')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('امتیاز نوبت')
        verbose_name_plural = _('امتیازهای نوبت')
    
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
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='cancellations', verbose_name='نوبت')
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_cancellations', verbose_name='لغو شده توسط')
    reason = models.CharField(max_length=20, choices=CANCELLATION_REASONS, verbose_name='دلیل')
    explanation = models.TextField(blank=True, null=True, verbose_name='توضیح')
    cancelled_at = models.DateTimeField(auto_now_add=True, verbose_name='لغو شده در')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ بازپرداخت')
    is_refunded = models.BooleanField(default=False, verbose_name='بازپرداخت شده')
    
    class Meta:
        verbose_name = _('لغو نوبت')
        verbose_name_plural = _('لغوهای نوبت')
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
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='reminders', verbose_name='نوبت')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, verbose_name='نوع یادآوری')
    scheduled_time = models.DateTimeField(verbose_name='زمان برنامه‌ریزی شده')
    is_sent = models.BooleanField(default=False, verbose_name='ارسال شده')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='ارسال شده در')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('یادآوری نوبت')
        verbose_name_plural = _('یادآوری‌های نوبت')
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"Reminder for {self.session} - {self.get_reminder_type_display()}"


class SessionBooking(models.Model):
    """Session booking requests (therapist confirmation required)"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    ]
    
    SESSION_MODES = [
        ('online', _('Online')),
        ('in_person', _('In Person')),
        ('phone', _('Phone Call')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_bookings', verbose_name='کاربر')
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='booking_requests', verbose_name='درمانگر')
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE, related_name='bookings', verbose_name='نوع نوبت')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    mode = models.CharField(max_length=20, choices=SESSION_MODES, verbose_name='حالت')
    
    # Preferred scheduling
    preferred_date = models.DateField(verbose_name='تاریخ ترجیحی')
    preferred_time = models.TimeField(verbose_name='زمان ترجیحی')
    alternative_dates = models.JSONField(default=list, verbose_name='تاریخ‌های جایگزین')
    
    # Session details
    goals = models.TextField(blank=True, null=True, verbose_name='اهداف جلسه')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های اضافی')
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='مکان')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    
    # Confirmation details
    confirmed_date = models.DateField(blank=True, null=True, verbose_name='تاریخ تأیید شده')
    confirmed_time = models.TimeField(blank=True, null=True, verbose_name='زمان تأیید شده')
    confirmation_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های تأیید')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='تأیید شده در')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='confirmed_bookings', verbose_name='تأیید شده توسط')
    
    # Croom integration
    croom_class_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه کلاس Croom')
    croom_class_url = models.URLField(blank=True, null=True, verbose_name='لینک کلاس Croom')
    croom_meeting_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه جلسه Croom')
    croom_password = models.CharField(max_length=50, blank=True, null=True, verbose_name='رمز عبور Croom')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    expires_at = models.DateTimeField(verbose_name='انقضا در')
    
    class Meta:
        verbose_name = _('درخواست نوبت')
        verbose_name_plural = _('درخواست‌های نوبت')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking by {self.user.full_name} with {self.therapist.full_name} - {self.preferred_date}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def confirm_booking(self, confirmed_date, confirmed_time, confirmed_by, notes=''):
        """Confirm the booking and create session"""
        from django.utils import timezone
        
        self.status = 'confirmed'
        self.confirmed_date = confirmed_date
        self.confirmed_time = confirmed_time
        self.confirmed_by = confirmed_by
        self.confirmation_notes = notes
        self.confirmed_at = timezone.now()
        self.save()
        
        # Create the actual session
        session = Session.objects.create(
            client=self.user,
            therapist=self.therapist,
            session_type=self.session_type,
            status='scheduled',
            mode=self.mode,
            scheduled_date=confirmed_date,
            scheduled_time=confirmed_time,
            duration_minutes=self.session_type.duration_minutes,
            location=self.location,
            goals=self.goals,
            price=self.price,
            meeting_link=self.croom_class_url,
            meeting_id=self.croom_meeting_id,
            meeting_password=self.croom_password
        )
        
        return session