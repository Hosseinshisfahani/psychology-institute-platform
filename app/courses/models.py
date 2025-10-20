from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class CourseCategory(models.Model):
    """Categories for courses"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name='نامک')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class'), verbose_name='کلاس آیکون Font Awesome')
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code'), verbose_name='کد رنگ هگز')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('دسته‌بندی دوره')
        verbose_name_plural = _('دسته‌بندی‌های دوره')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """Psychological courses"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='نامک')
    description = models.TextField(verbose_name='توضیحات')
    short_description = models.CharField(max_length=300, verbose_name='توضیحات کوتاه')
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses', verbose_name='دسته‌بندی')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses', verbose_name='مربی')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name='سطح دشواری')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='وضعیت')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='قیمت تخفیف')
    is_free = models.BooleanField(default=False, verbose_name='رایگان')
    
    # Course details
    duration_hours = models.PositiveIntegerField(verbose_name='مدت ساعت')
    language = models.CharField(max_length=10, default='fa', verbose_name='زبان')
    level = models.CharField(max_length=50, verbose_name='سطح')
    prerequisites = models.TextField(blank=True, null=True, verbose_name='پیش‌نیازها')
    learning_objectives = models.TextField(verbose_name='اهداف یادگیری')
    
    # Media
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True, verbose_name='تصویر کوچک')
    video_intro = models.FileField(upload_to='courses/videos/', blank=True, null=True, verbose_name='ویدیو معرفی')
    
    # Statistics
    enrollment_count = models.PositiveIntegerField(default=0, verbose_name='تعداد ثبت‌نام')
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='امتیاز')
    review_count = models.PositiveIntegerField(default=0, verbose_name='تعداد نظر')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انتشار')
    
    class Meta:
        verbose_name = _('دوره')
        verbose_name_plural = _('دوره‌ها')
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


class CourseModule(models.Model):
    """Modules within a course"""
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name='دوره')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    is_required = models.BooleanField(default=True, verbose_name='اجباری')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('ماژول دوره')
        verbose_name_plural = _('ماژول‌های دوره')
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"


class Lesson(models.Model):
    """Lessons within course modules"""
    
    LESSON_TYPES = [
        ('video', _('Video')),
        ('text', _('Text')),
        ('quiz', _('Quiz')),
        ('assignment', _('Assignment')),
        ('live', _('Live Session')),
    ]
    
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons', verbose_name='ماژول')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, verbose_name='نوع درس')
    content = models.TextField(blank=True, null=True, verbose_name='محتوای')
    video_file = models.FileField(upload_to='courses/lessons/videos/', blank=True, null=True, verbose_name='فایل ویدیو')
    video_url = models.URLField(blank=True, null=True, verbose_name='لینک ویدیو')
    duration_minutes = models.PositiveIntegerField(blank=True, null=True, verbose_name='مدت دقیقه')
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    is_preview = models.BooleanField(default=False, verbose_name='پیش‌نمایش')
    is_required = models.BooleanField(default=True, verbose_name='اجباری')
    allow_download = models.BooleanField(default=False, verbose_name='اجازه دانلود')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('درس')
        verbose_name_plural = _('درس‌ها')
        ordering = ['order']
        unique_together = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.course.title} - {self.title}"


class Enrollment(models.Model):
    """Course enrollments"""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('dropped', _('Dropped')),
        ('suspended', _('Suspended')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name='کاربر')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='دوره')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='وضعیت')
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت‌نام')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    progress_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='درصد پیشرفت')
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name='آخرین دسترسی')
    
    class Meta:
        verbose_name = _('ثبت‌نام')
        verbose_name_plural = _('ثبت‌نام‌ها')
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.full_name} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    """User progress on individual lessons"""
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress', verbose_name='ثبت‌نام')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress', verbose_name='درس')
    is_completed = models.BooleanField(default=False, verbose_name='تکمیل شده')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    time_spent = models.PositiveIntegerField(default=0, help_text=_('Time spent in seconds'), verbose_name='زمان صرف شده')
    last_position = models.PositiveIntegerField(default=0, help_text=_('Last position in video (seconds)'), verbose_name='آخرین موقعیت')
    
    class Meta:
        verbose_name = _('پیشرفت درس')
        verbose_name_plural = _('پیشرفت درس‌ها')
        unique_together = ['enrollment', 'lesson']
    
    def __str__(self):
        return f"{self.enrollment.user.full_name} - {self.lesson.title}"


class CourseReview(models.Model):
    """Course reviews and ratings"""
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='review', verbose_name='ثبت‌نام')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز')
    title = models.CharField(max_length=200, verbose_name='عنوان نظر')
    content = models.TextField(verbose_name='محتوای نظر')
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('نظر دوره')
        verbose_name_plural = _('نظرات دوره‌ها')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.enrollment.course.title} by {self.enrollment.user.full_name}"


class Coupon(models.Model):
    """Discount coupons for courses"""
    
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
    
    # Applicable courses
    applicable_courses = models.ManyToManyField(Course, blank=True, related_name='coupons', verbose_name='دوره‌های قابل اعمال')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('کوپن تخفیف')
        verbose_name_plural = _('کوپن‌های تخفیف')
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


class CoursePurchase(models.Model):
    """Course purchases"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_purchases', verbose_name='کاربر')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases', verbose_name='دوره')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ پرداخت شده')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='قیمت اصلی')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ تخفیف')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='کوپن استفاده شده')
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ خرید')
    payment_method = models.CharField(max_length=50, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    order = models.ForeignKey('payment.Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='سفارش')
    
    class Meta:
        verbose_name = _('خرید دوره')
        verbose_name_plural = _('خریدهای دوره‌ها')
        ordering = ['-purchased_at']
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.full_name} purchased {self.course.title}"