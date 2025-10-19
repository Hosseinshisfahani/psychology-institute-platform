from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from app.courses.models import Course, Enrollment

User = get_user_model()


class PackageCategory(models.Model):
    """Categories for packages"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name='نامک')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class', verbose_name='کلاس آیکون Font Awesome'))
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code', verbose_name='کد رنگ هگز'))
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('دسته‌بندی پکیج')
        verbose_name_plural = _('دسته‌بندی‌های پکیج')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Package(models.Model):
    """Educational packages containing multiple courses"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='نامک')
    description = models.TextField(verbose_name='توضیحات')
    short_description = models.CharField(max_length=300, verbose_name='توضیحات کوتاه')
    category = models.ForeignKey(PackageCategory, on_delete=models.CASCADE, related_name='packages', verbose_name='دسته‌بندی')
    
    # Courses
    courses = models.ManyToManyField(Course, related_name='packages', verbose_name='دوره‌ها')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='وضعیت')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='قیمت تخفیف')
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    
    # Package details
    duration_months = models.PositiveIntegerField(verbose_name='مدت ماه', help_text='زمان تخمینی تکمیل')
    language = models.CharField(max_length=10, default='fa', verbose_name='زبان')
    prerequisites = models.TextField(blank=True, null=True, verbose_name='پیش‌نیازها')
    learning_objectives = models.TextField(verbose_name='اهداف یادگیری')
    
    # Media
    thumbnail = models.ImageField(upload_to='packages/thumbnails/', blank=True, null=True, verbose_name='تصویر کوچک')
    intro_video = models.FileField(upload_to='packages/videos/', blank=True, null=True, verbose_name='ویدیو معرفی')
    
    # Statistics
    purchase_count = models.PositiveIntegerField(default=0, verbose_name='تعداد خرید')
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='امتیاز')
    review_count = models.PositiveIntegerField(default=0, verbose_name='تعداد نظر')
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True, verbose_name='عنوان متا')
    meta_description = models.TextField(blank=True, null=True, verbose_name='توضیحات متا')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انتشار')
    
    class Meta:
        verbose_name = _('پکیج')
        verbose_name_plural = _('پکیج‌ها')
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
    def total_courses(self):
        return self.courses.count()
    
    @property
    def total_hours(self):
        """Calculate total hours from all courses"""
        return sum(course.duration_hours for course in self.courses.all())
    
    @property
    def original_total_price(self):
        """Calculate total price if courses bought individually"""
        return sum(course.current_price for course in self.courses.all())
    
    @property
    def savings_amount(self):
        """Calculate savings when buying package vs individual courses"""
        original = self.original_total_price
        return original - self.current_price if original > self.current_price else 0
    
    @property
    def savings_percentage(self):
        """Calculate savings percentage"""
        original = self.original_total_price
        if original > 0:
            return int((self.savings_amount / original) * 100)
        return 0


class PackagePurchase(models.Model):
    """Package purchases by users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='package_purchases', verbose_name='کاربر')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='purchases', verbose_name='پکیج')
    
    # Pricing
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ پرداخت شده')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='قیمت اصلی')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ تخفیف')
    
    # Payment details
    payment_method = models.CharField(max_length=50, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    order = models.ForeignKey('payment.Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='سفارش')
    
    # Timestamps
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ خرید')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضا')
    
    class Meta:
        verbose_name = _('خرید پکیج')
        verbose_name_plural = _('خریدهای پکیج')
        ordering = ['-purchased_at']
        unique_together = ['user', 'package']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.package.title}"
    
    def create_course_enrollments(self):
        """Create enrollment records for all courses in the package"""
        from django.utils import timezone
        
        for course in self.package.courses.all():
            # Create enrollment if it doesn't exist
            enrollment, created = Enrollment.objects.get_or_create(
                user=self.user,
                course=course,
                defaults={
                    'status': 'active',
                    'enrolled_at': timezone.now(),
                }
            )
            
            # Link enrollment to package purchase
            PackageEnrollment.objects.get_or_create(
                purchase=self,
                enrollment=enrollment
            )
    
    @property
    def is_expired(self):
        """Check if package access has expired"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False


class PackageEnrollment(models.Model):
    """Track user progress in package courses"""
    
    purchase = models.ForeignKey(PackagePurchase, on_delete=models.CASCADE, related_name='course_enrollments', verbose_name='خرید')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='package_enrollments', verbose_name='ثبت‌نام')
    
    # Progress tracking
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='شروع شده در')
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name='آخرین دسترسی')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('ثبت‌نام پکیج')
        verbose_name_plural = _('ثبت‌نام‌های پکیج')
        unique_together = ['purchase', 'enrollment']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.purchase.user.full_name} - {self.enrollment.course.title}"
    
    @property
    def progress_percentage(self):
        """Get progress percentage from enrollment"""
        return self.enrollment.progress_percentage


class PackageProgress(models.Model):
    """Overall package progress for a user"""
    
    purchase = models.OneToOneField(PackagePurchase, on_delete=models.CASCADE, related_name='progress', verbose_name='خرید')
    overall_progress_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='پیشرفت کلی')
    completed_courses = models.PositiveIntegerField(default=0, verbose_name='دوره‌های تکمیل شده')
    total_time_spent = models.PositiveIntegerField(default=0, help_text=_('Time spent in minutes'), verbose_name='کل زمان صرف شده')
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('پیشرفت پکیج')
        verbose_name_plural = _('پیشرفت‌های پکیج')
    
    def __str__(self):
        return f"Progress for {self.purchase}"
    
    def calculate_progress(self):
        """Calculate overall progress based on course enrollments"""
        enrollments = self.purchase.course_enrollments.all()
        if enrollments.count() > 0:
            total_progress = sum(e.enrollment.progress_percentage for e in enrollments)
            self.overall_progress_percentage = total_progress / enrollments.count()
            self.completed_courses = enrollments.filter(enrollment__status='completed').count()
            self.save()


class PackageReview(models.Model):
    """Package reviews and ratings"""
    
    purchase = models.OneToOneField(PackagePurchase, on_delete=models.CASCADE, related_name='review', verbose_name='خرید')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز')
    title = models.CharField(max_length=200, verbose_name='عنوان نظر')
    content = models.TextField(verbose_name='محتوای نظر')
    
    # Detailed ratings
    value_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='ارزش پول')
    content_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='کیفیت محتوا')
    support_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز پشتیبانی')
    
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('نظر پکیج')
        verbose_name_plural = _('نظرات پکیج')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.purchase.package.title} by {self.purchase.user.full_name}"


class PackageCoupon(models.Model):
    """Discount coupons specifically for packages"""
    
    COUPON_TYPES = [
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name='کد کوپن')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES, verbose_name='نوع کوپن')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مقدار تخفیف')
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='حداقل مبلغ سفارش')
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='حداکثر مبلغ تخفیف')
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(blank=True, null=True, verbose_name='حد استفاده')
    used_count = models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده')
    
    # Validity
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    valid_from = models.DateTimeField(verbose_name='معتبر از')
    valid_until = models.DateTimeField(verbose_name='معتبر تا')
    
    # Applicable packages
    applicable_packages = models.ManyToManyField(Package, blank=True, related_name='coupons', verbose_name='پکیج‌های قابل اعمال')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('کوپن پکیج')
        verbose_name_plural = _('کوپن‌های پکیج')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )
    
    def calculate_discount(self, order_amount):
        """Calculate discount amount for given order amount"""
        if not self.is_valid() or order_amount < self.min_order_amount:
            return 0
        
        if self.coupon_type == 'percentage':
            discount = (order_amount * self.discount_value) / 100
        else:  # fixed
            discount = self.discount_value
        
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
        
        return min(discount, order_amount)
