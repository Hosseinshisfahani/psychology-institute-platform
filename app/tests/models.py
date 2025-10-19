from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

User = get_user_model()


class TestCategory(models.Model):
    """Categories for psychological tests"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class'))
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code'))
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('دسته‌بندی تست')
        verbose_name_plural = _('دسته‌بندی‌های تست')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from name, with fallback for Persian text
            if self.name == 'شخصیت':
                self.slug = 'personality'
            elif self.name == 'هوش':
                self.slug = 'intelligence'
            else:
                # Try to slugify, if empty use a generic slug
                slug = slugify(self.name)
                if not slug:
                    slug = f'category-{self.id or "new"}'
                self.slug = slug
        super().save(*args, **kwargs)


class PsychologicalTest(models.Model):
    """Psychological tests available for users"""
    
    DIFFICULTY_CHOICES = [
        ('easy', _('Easy')),
        ('medium', _('Medium')),
        ('hard', _('Hard')),
    ]
    
    TEST_TYPES = [
        ('personality', _('Personality')),
        ('cognitive', _('Cognitive')),
        ('emotional', _('Emotional')),
        ('behavioral', _('Behavioral')),
        ('clinical', _('Clinical')),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='tests', verbose_name='دسته‌بندی')
    test_type = models.CharField(max_length=20, choices=TEST_TYPES, verbose_name='نوع تست')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name='سطح دشواری')
    estimated_duration = models.PositiveIntegerField(help_text='مدت (دقیقه)', verbose_name='مدت تخمینی')
    instructions = models.TextField(verbose_name='دستورالعمل‌ها')
    is_free = models.BooleanField(default=True, verbose_name='رایگان')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='قیمت')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    requires_therapist = models.BooleanField(default=False, verbose_name='نیاز به درمانگر')
    min_age = models.PositiveIntegerField(default=0, verbose_name='حداقل سن')
    max_age = models.PositiveIntegerField(default=100, verbose_name='حداکثر سن')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests', verbose_name='ایجاد شده توسط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('تست روانشناسی')
        verbose_name_plural = _('تست‌های روانشناسی')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Question(models.Model):
    """Questions for psychological tests"""
    
    QUESTION_TYPES = [
        ('single_choice', _('Single Choice')),
        ('multiple_choice', _('Multiple Choice')),
        ('likert_scale', _('Likert Scale')),
        ('text', _('Text Input')),
        ('number', _('Number Input')),
    ]
    
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='questions', verbose_name='تست')
    question_text = models.TextField(verbose_name='متن سوال')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name='نوع سوال')
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    is_required = models.BooleanField(default=True, verbose_name='اجباری')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('سوال')
        verbose_name_plural = _('سوالات')
        ordering = ['order']
        unique_together = ['test', 'order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Choice(models.Model):
    """Answer choices for questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name='سوال')
    choice_text = models.CharField(max_length=200, verbose_name='متن گزینه')
    value = models.CharField(max_length=50, verbose_name='مقدار')
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    score = models.IntegerField(default=0, verbose_name='امتیاز')
    
    class Meta:
        verbose_name = _('گزینه')
        verbose_name_plural = _('گزینه‌ها')
        ordering = ['order']
        unique_together = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.choice_text}"


class TestSession(models.Model):
    """User test sessions"""
    
    STATUS_CHOICES = [
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('abandoned', _('Abandoned')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_sessions', verbose_name='کاربر')
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='sessions', verbose_name='تست')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name='وضعیت')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='شروع شده در')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تکمیل شده در')
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='سوال فعلی')
    
    class Meta:
        verbose_name = _('جلسه تست')
        verbose_name_plural = _('جلسات تست')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.test.title}"


class Answer(models.Model):
    """User answers to test questions"""
    
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='answers', verbose_name='جلسه')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='سوال')
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name='answers', verbose_name='گزینه‌های انتخاب شده')
    text_answer = models.TextField(blank=True, null=True, verbose_name='پاسخ متنی')
    number_answer = models.FloatField(blank=True, null=True, verbose_name='پاسخ عددی')
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ پاسخ')
    
    class Meta:
        verbose_name = _('پاسخ')
        verbose_name_plural = _('پاسخ‌ها')
        unique_together = ['session', 'question']
    
    def __str__(self):
        return f"Answer for {self.question.question_text[:30]}..."


class TestResult(models.Model):
    """Results of completed tests"""
    
    session = models.OneToOneField(TestSession, on_delete=models.CASCADE, related_name='result', verbose_name='جلسه')
    total_score = models.FloatField(verbose_name='امتیاز کل')
    max_score = models.FloatField(verbose_name='حداکثر امتیاز')
    percentage = models.FloatField(verbose_name='درصد')
    interpretation = models.TextField(verbose_name='تفسیر')
    recommendations = models.TextField(blank=True, null=True, verbose_name='توصیه‌ها')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تولید')
    
    class Meta:
        verbose_name = _('نتیجه تست')
        verbose_name_plural = _('نتایج تست')
    
    def __str__(self):
        return f"Result for {self.session.user.full_name} - {self.session.test.title}"


class TestPurchase(models.Model):
    """Purchases of paid tests"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_purchases', verbose_name='کاربر')
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='purchases', verbose_name='تست')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ پرداخت شده')
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ خرید')
    payment_method = models.CharField(max_length=50, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    
    class Meta:
        verbose_name = _('خرید تست')
        verbose_name_plural = _('خریدهای تست')
        ordering = ['-purchased_at']
        unique_together = ['user', 'test']
    
    def __str__(self):
        return f"{self.user.full_name} purchased {self.test.title}"