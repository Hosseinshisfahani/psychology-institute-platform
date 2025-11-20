from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class WorkshopCategory(models.Model):
    """Categories for workshops"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name='نامک')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class'), verbose_name='کلاس آیکون Font Awesome')
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code'), verbose_name='کد رنگ هگز')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('دسته‌بندی کارگاه')
        verbose_name_plural = _('دسته‌بندی‌های کارگاه')
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
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='نامک')
    description = models.TextField(verbose_name='توضیحات')
    short_description = models.CharField(max_length=300, verbose_name='توضیحات کوتاه')
    category = models.ForeignKey(WorkshopCategory, on_delete=models.CASCADE, related_name='workshops', verbose_name='دسته‌بندی')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_workshops', verbose_name='مدرس')
    
    # Status and difficulty
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='وضعیت')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name='سطح دشواری')
    
    # Scheduling
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    registration_deadline = models.DateTimeField(verbose_name='مهلت ثبت‌نام')
    
    # Capacity
    max_participants = models.PositiveIntegerField(default=50, verbose_name='حداکثر شرکت‌کنندگان')
    current_participants = models.PositiveIntegerField(default=0, verbose_name='شرکت‌کنندگان فعلی')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='قیمت تخفیف')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='both', verbose_name='نوع پرداخت')
    
    # Installment options
    installment_months = models.PositiveIntegerField(default=3, verbose_name='تعداد ماه‌های اقساط')
    
    # Workshop details
    total_hours = models.PositiveIntegerField(verbose_name='مجموع ساعات')
    language = models.CharField(max_length=10, default='fa', verbose_name='زبان')
    prerequisites = models.TextField(blank=True, null=True, verbose_name='پیش‌نیازها')
    learning_objectives = models.TextField(verbose_name='اهداف یادگیری')
    
    # Media
    thumbnail = models.ImageField(upload_to='workshops/thumbnails/', blank=True, null=True, verbose_name='تصویر کوچک')
    intro_video = models.FileField(upload_to='workshops/videos/', blank=True, null=True, verbose_name='ویدیو معرفی')
    
    # Statistics
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='امتیاز')
    review_count = models.PositiveIntegerField(default=0, verbose_name='تعداد نظرات')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انتشار')
    
    class Meta:
        verbose_name = _('کارگاه')
        verbose_name_plural = _('کارگاه‌ها')
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
    
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='sessions', verbose_name='کارگاه')
    session_number = models.PositiveIntegerField(verbose_name='شماره جلسه')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    
    # Scheduling
    scheduled_datetime = models.DateTimeField(verbose_name='تاریخ و زمان برنامه‌ریزی شده')
    duration_minutes = models.PositiveIntegerField(verbose_name='مدت دقیقه')
    
    # Video and Croom platform links
    session_video = models.FileField(upload_to='workshops/session_videos/', blank=True, null=True, verbose_name='ویدیو جلسه')
    croom_platform_link = models.URLField(blank=True, null=True, verbose_name='لینک پلتفرم سی‌روم')
    
    # Session materials
    materials = models.TextField(blank=True, null=True, verbose_name='مواد جلسه')
    homework = models.TextField(blank=True, null=True, verbose_name='تکلیف')
    
    # Status
    is_completed = models.BooleanField(default=False, verbose_name='تکمیل شده')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تکمیل شده در')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('جلسه کارگاه')
        verbose_name_plural = _('جلسات کارگاه')
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workshop_registrations', verbose_name='کاربر')
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='registrations', verbose_name='کارگاه')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment', verbose_name='وضعیت')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name='نوع پرداخت')
    
    # Pricing
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ پرداخت شده')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ کل')
    
    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='ثبت‌نام شده در')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تکمیل شده در')
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name='آخرین دسترسی')
    
    # Progress
    progress_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='درصد پیشرفت')
    
    class Meta:
        verbose_name = _('ثبت‌نام کارگاه')
        verbose_name_plural = _('ثبت‌نام‌های کارگاه')
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
    
    registration = models.ForeignKey(WorkshopRegistration, on_delete=models.CASCADE, related_name='session_attendance', verbose_name='ثبت‌نام')
    session = models.ForeignKey(WorkshopSession, on_delete=models.CASCADE, related_name='attendance', verbose_name='جلسه')
    attended = models.BooleanField(default=False, verbose_name='حاضر')
    attendance_marked_at = models.DateTimeField(blank=True, null=True, verbose_name='حضور ثبت شده در')
    
    # Time tracking
    join_time = models.DateTimeField(blank=True, null=True, verbose_name='زمان ورود')
    leave_time = models.DateTimeField(blank=True, null=True, verbose_name='زمان خروج')
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name='مدت دقیقه')
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('حضور جلسه کارگاه')
        verbose_name_plural = _('حضورهای جلسه کارگاه')
        unique_together = ['registration', 'session']
        ordering = ['session__scheduled_datetime']
    
    def __str__(self):
        return f"{self.registration.user.full_name} - {self.session.title}"


class InstallmentPlan(models.Model):
    """Installment plan for a workshop registration"""
    
    registration = models.OneToOneField(WorkshopRegistration, on_delete=models.CASCADE, related_name='installment_plan', verbose_name='ثبت‌نام')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ کل')
    number_of_installments = models.PositiveIntegerField(verbose_name='تعداد اقساط')
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ قسط')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('برنامه اقساط')
        verbose_name_plural = _('برنامه‌های اقساط')
    
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
    
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='payments', verbose_name='برنامه')
    installment_number = models.PositiveIntegerField(verbose_name='شماره قسط')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ')
    due_date = models.DateField(verbose_name='تاریخ سررسید')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # Payment details
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='پرداخت شده در')
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    order = models.ForeignKey('payment.Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='سفارش')
    
    # Reminders
    reminder_sent = models.BooleanField(default=False, verbose_name='یادآوری ارسال شده')
    reminder_sent_at = models.DateTimeField(blank=True, null=True, verbose_name='یادآوری ارسال شده در')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('پرداخت اقساط')
        verbose_name_plural = _('پرداخت‌های اقساط')
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
    
    registration = models.OneToOneField(WorkshopRegistration, on_delete=models.CASCADE, related_name='review', verbose_name='ثبت‌نام')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز')
    title = models.CharField(max_length=200, verbose_name='عنوان نظر')
    content = models.TextField(verbose_name='محتوای نظر')
    
    # Detailed ratings
    instructor_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز مدرس')
    content_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز محتوا')
    interaction_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز تعامل')
    
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('نظر کارگاه')
        verbose_name_plural = _('نظرات کارگاه')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.registration.workshop.title} by {self.registration.user.full_name}"


class WorkshopCertificate(models.Model):
    """Certificates issued to users who complete workshops"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('issued', _('Issued')),
        ('revoked', _('Revoked')),
    ]
    
    registration = models.OneToOneField(
        WorkshopRegistration,
        on_delete=models.CASCADE,
        related_name='certificate',
        verbose_name='ثبت‌نام'
    )
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='شماره گواهینامه'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # Certificate file
    certificate_file = models.FileField(
        upload_to='workshops/certificates/',
        blank=True,
        null=True,
        verbose_name='فایل گواهینامه'
    )
    
    # Issue details
    issued_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ صدور'
    )
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='issued_certificates',
        verbose_name='صادرکننده'
    )
    
    # Revocation details
    revoked_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ لغو'
    )
    revocation_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='دلیل لغو'
    )
    
    # Verification
    verification_code = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='کد تأیید'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    class Meta:
        verbose_name = _('گواهینامه کارگاه')
        verbose_name_plural = _('گواهینامه‌های کارگاه')
        ordering = ['-issued_at', '-created_at']
    
    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.registration.user.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate unique certificate number
            from django.utils import timezone
            import random
            import string
            
            # Format: WS-YYYYMMDD-XXXXXX (6 random alphanumeric)
            date_str = timezone.now().strftime('%Y%m%d')
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.certificate_number = f"WS-{date_str}-{random_suffix}"
            
            # Ensure uniqueness
            while WorkshopCertificate.objects.filter(certificate_number=self.certificate_number).exists():
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                self.certificate_number = f"WS-{date_str}-{random_suffix}"
        
        if not self.verification_code:
            import secrets
            self.verification_code = secrets.token_urlsafe(16)
            
            # Ensure uniqueness
            while WorkshopCertificate.objects.filter(verification_code=self.verification_code).exists():
                self.verification_code = secrets.token_urlsafe(16)
        
        if self.status == 'issued' and not self.issued_at:
            from django.utils import timezone
            self.issued_at = timezone.now()
        
        if self.status == 'revoked' and not self.revoked_at:
            from django.utils import timezone
            self.revoked_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_valid(self):
        """Check if certificate is valid (issued and not revoked)"""
        return self.status == 'issued'
    
    @property
    def user(self):
        """Get the user who owns this certificate"""
        return self.registration.user
    
    @property
    def workshop(self):
        """Get the workshop this certificate is for"""
        return self.registration.workshop
