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
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Test Category')
        verbose_name_plural = _('Test Categories')
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
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='tests', verbose_name=_('Category'))
    test_type = models.CharField(max_length=20, choices=TEST_TYPES, verbose_name=_('Test Type'))
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name=_('Difficulty'))
    estimated_duration = models.PositiveIntegerField(help_text=_('Duration in minutes'), verbose_name=_('Estimated Duration'))
    instructions = models.TextField(verbose_name=_('Instructions'))
    is_free = models.BooleanField(default=True, verbose_name=_('Is Free'))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Price'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    requires_therapist = models.BooleanField(default=False, verbose_name=_('Requires Therapist'))
    min_age = models.PositiveIntegerField(default=0, verbose_name=_('Minimum Age'))
    max_age = models.PositiveIntegerField(default=100, verbose_name=_('Maximum Age'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Psychological Test')
        verbose_name_plural = _('Psychological Tests')
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
    
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='questions', verbose_name=_('Test'))
    question_text = models.TextField(verbose_name=_('Question Text'))
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name=_('Question Type'))
    order = models.PositiveIntegerField(verbose_name=_('Order'))
    is_required = models.BooleanField(default=True, verbose_name=_('Is Required'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['order']
        unique_together = ['test', 'order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Choice(models.Model):
    """Answer choices for questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name=_('Question'))
    choice_text = models.CharField(max_length=200, verbose_name=_('Choice Text'))
    value = models.CharField(max_length=50, verbose_name=_('Value'))
    order = models.PositiveIntegerField(verbose_name=_('Order'))
    score = models.IntegerField(default=0, verbose_name=_('Score'))
    
    class Meta:
        verbose_name = _('Choice')
        verbose_name_plural = _('Choices')
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_sessions', verbose_name=_('User'))
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='sessions', verbose_name=_('Test'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name=_('Status'))
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Started At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Current Question'))
    
    class Meta:
        verbose_name = _('Test Session')
        verbose_name_plural = _('Test Sessions')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.test.title}"


class Answer(models.Model):
    """User answers to test questions"""
    
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='answers', verbose_name=_('Session'))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name=_('Question'))
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name='answers', verbose_name=_('Selected Choices'))
    text_answer = models.TextField(blank=True, null=True, verbose_name=_('Text Answer'))
    number_answer = models.FloatField(blank=True, null=True, verbose_name=_('Number Answer'))
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Answered At'))
    
    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        unique_together = ['session', 'question']
    
    def __str__(self):
        return f"Answer for {self.question.question_text[:30]}..."


class TestResult(models.Model):
    """Results of completed tests"""
    
    session = models.OneToOneField(TestSession, on_delete=models.CASCADE, related_name='result', verbose_name=_('Session'))
    total_score = models.FloatField(verbose_name=_('Total Score'))
    max_score = models.FloatField(verbose_name=_('Maximum Score'))
    percentage = models.FloatField(verbose_name=_('Percentage'))
    interpretation = models.TextField(verbose_name=_('Interpretation'))
    recommendations = models.TextField(blank=True, null=True, verbose_name=_('Recommendations'))
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Generated At'))
    
    class Meta:
        verbose_name = _('Test Result')
        verbose_name_plural = _('Test Results')
    
    def __str__(self):
        return f"Result for {self.session.user.full_name} - {self.session.test.title}"


class TestPurchase(models.Model):
    """Purchases of paid tests"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_purchases', verbose_name=_('User'))
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='purchases', verbose_name=_('Test'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount Paid'))
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Purchased At'))
    payment_method = models.CharField(max_length=50, verbose_name=_('Payment Method'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Transaction ID'))
    
    class Meta:
        verbose_name = _('Test Purchase')
        verbose_name_plural = _('Test Purchases')
        ordering = ['-purchased_at']
        unique_together = ['user', 'test']
    
    def __str__(self):
        return f"{self.user.full_name} purchased {self.test.title}"