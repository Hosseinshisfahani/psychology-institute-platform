from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class CourseCategory(models.Model):
    """Categories for courses"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class'))
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Course Category')
        verbose_name_plural = _('Course Categories')
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
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Slug'))
    description = models.TextField(verbose_name=_('Description'))
    short_description = models.CharField(max_length=300, verbose_name=_('Short Description'))
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses', verbose_name=_('Category'))
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses', verbose_name=_('Instructor'))
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name=_('Difficulty'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('Status'))
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Discount Price'))
    is_free = models.BooleanField(default=False, verbose_name=_('Is Free'))
    
    # Course details
    duration_hours = models.PositiveIntegerField(verbose_name=_('Duration (Hours)'))
    language = models.CharField(max_length=10, default='fa', verbose_name=_('Language'))
    level = models.CharField(max_length=50, verbose_name=_('Level'))
    prerequisites = models.TextField(blank=True, null=True, verbose_name=_('Prerequisites'))
    learning_objectives = models.TextField(verbose_name=_('Learning Objectives'))
    
    # Media
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True, verbose_name=_('Thumbnail'))
    video_intro = models.FileField(upload_to='courses/videos/', blank=True, null=True, verbose_name=_('Intro Video'))
    
    # Statistics
    enrollment_count = models.PositiveIntegerField(default=0, verbose_name=_('Enrollment Count'))
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name=_('Rating'))
    review_count = models.PositiveIntegerField(default=0, verbose_name=_('Review Count'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Published At'))
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
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
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name=_('Course'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    order = models.PositiveIntegerField(verbose_name=_('Order'))
    is_required = models.BooleanField(default=True, verbose_name=_('Is Required'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Course Module')
        verbose_name_plural = _('Course Modules')
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
    
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons', verbose_name=_('Module'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, verbose_name=_('Lesson Type'))
    content = models.TextField(blank=True, null=True, verbose_name=_('Content'))
    video_file = models.FileField(upload_to='courses/lessons/videos/', blank=True, null=True, verbose_name=_('Video File'))
    video_url = models.URLField(blank=True, null=True, verbose_name=_('Video URL'))
    duration_minutes = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Duration (Minutes)'))
    order = models.PositiveIntegerField(verbose_name=_('Order'))
    is_preview = models.BooleanField(default=False, verbose_name=_('Is Preview'))
    is_required = models.BooleanField(default=True, verbose_name=_('Is Required'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name=_('User'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name=_('Course'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('Status'))
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Enrolled At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    progress_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Progress Percentage'))
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name=_('Last Accessed'))
    
    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.full_name} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    """User progress on individual lessons"""
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress', verbose_name=_('Enrollment'))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress', verbose_name=_('Lesson'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Is Completed'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    time_spent = models.PositiveIntegerField(default=0, help_text=_('Time spent in seconds'), verbose_name=_('Time Spent'))
    last_position = models.PositiveIntegerField(default=0, help_text=_('Last position in video (seconds)'), verbose_name=_('Last Position'))
    
    class Meta:
        verbose_name = _('Lesson Progress')
        verbose_name_plural = _('Lesson Progress')
        unique_together = ['enrollment', 'lesson']
    
    def __str__(self):
        return f"{self.enrollment.user.full_name} - {self.lesson.title}"


class CourseReview(models.Model):
    """Course reviews and ratings"""
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='review', verbose_name=_('Enrollment'))
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Rating'))
    title = models.CharField(max_length=200, verbose_name=_('Review Title'))
    content = models.TextField(verbose_name=_('Review Content'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Is Approved'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Course Review')
        verbose_name_plural = _('Course Reviews')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.enrollment.course.title} by {self.enrollment.user.full_name}"


class CoursePurchase(models.Model):
    """Course purchases"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_purchases', verbose_name=_('User'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases', verbose_name=_('Course'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount Paid'))
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Purchased At'))
    payment_method = models.CharField(max_length=50, verbose_name=_('Payment Method'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Transaction ID'))
    
    class Meta:
        verbose_name = _('Course Purchase')
        verbose_name_plural = _('Course Purchases')
        ordering = ['-purchased_at']
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.full_name} purchased {self.course.title}"