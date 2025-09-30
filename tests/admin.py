from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    TestCategory, PsychologicalTest, Question, Choice, 
    TestSession, Answer, TestResult, TestPurchase
)


class ChoiceInline(admin.TabularInline):
    """Inline admin for question choices"""
    model = Choice
    extra = 0
    fields = ['choice_text', 'value', 'order', 'score']


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for TestCategory model"""
    
    list_display = ('name', 'color', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)


@admin.register(PsychologicalTest)
class PsychologicalTestAdmin(admin.ModelAdmin):
    """Admin configuration for PsychologicalTest model"""
    
    list_display = ('title', 'category', 'test_type', 'difficulty', 'is_free', 'price', 'is_active', 'created_at')
    list_filter = ('test_type', 'difficulty', 'is_free', 'is_active', 'requires_therapist', 'category', 'created_at')
    search_fields = ('title', 'description', 'created_by__first_name', 'created_by__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category', 'created_by')
        }),
        (_('Test Configuration'), {
            'fields': ('test_type', 'difficulty', 'estimated_duration', 'instructions')
        }),
        (_('Pricing'), {
            'fields': ('is_free', 'price')
        }),
        (_('Requirements'), {
            'fields': ('requires_therapist', 'min_age', 'max_age')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Question model"""
    
    list_display = ('test', 'question_text_short', 'question_type', 'order', 'is_required')
    list_filter = ('question_type', 'is_required', 'test__category', 'test')
    search_fields = ('question_text', 'test__title')
    ordering = ('test', 'order')
    inlines = [ChoiceInline]
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = _('Question Text')


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Choice model"""
    
    list_display = ('question', 'choice_text_short', 'value', 'order', 'score')
    list_filter = ('question__test', 'question__question_type')
    search_fields = ('choice_text', 'question__question_text')
    ordering = ('question__test', 'question__order', 'order')
    
    def choice_text_short(self, obj):
        return obj.choice_text[:30] + '...' if len(obj.choice_text) > 30 else obj.choice_text
    choice_text_short.short_description = _('Choice Text')


class AnswerInline(admin.TabularInline):
    """Inline admin for test session answers"""
    model = Answer
    extra = 0
    readonly_fields = ('question', 'selected_choices', 'text_answer', 'number_answer', 'answered_at')
    can_delete = False


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    """Admin configuration for TestSession model"""
    
    list_display = ('user', 'test', 'status', 'started_at', 'completed_at', 'current_question')
    list_filter = ('status', 'started_at', 'completed_at', 'test__category')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'test__title')
    readonly_fields = ('started_at', 'completed_at')
    inlines = [AnswerInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'test', 'status')
        }),
        (_('Progress'), {
            'fields': ('current_question',)
        }),
        (_('Timestamps'), {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin configuration for Answer model"""
    
    list_display = ('session', 'question_short', 'answer_summary', 'answered_at')
    list_filter = ('session__test', 'question__question_type', 'answered_at')
    search_fields = ('session__user__first_name', 'session__user__last_name', 'question__question_text')
    readonly_fields = ('answered_at',)
    
    def question_short(self, obj):
        return obj.question.question_text[:30] + '...' if len(obj.question.question_text) > 30 else obj.question.question_text
    question_short.short_description = _('Question')
    
    def answer_summary(self, obj):
        if obj.selected_choices.exists():
            return ', '.join([choice.choice_text for choice in obj.selected_choices.all()[:2]])
        elif obj.text_answer:
            return obj.text_answer[:30] + '...' if len(obj.text_answer) > 30 else obj.text_answer
        elif obj.number_answer:
            return str(obj.number_answer)
        return '-'
    answer_summary.short_description = _('Answer')


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    """Admin configuration for TestResult model"""
    
    list_display = ('session', 'total_score', 'max_score', 'percentage', 'generated_at')
    list_filter = ('generated_at', 'session__test__category')
    search_fields = ('session__user__first_name', 'session__user__last_name', 'session__test__title')
    readonly_fields = ('generated_at',)
    
    fieldsets = (
        (None, {
            'fields': ('session',)
        }),
        (_('Scores'), {
            'fields': ('total_score', 'max_score', 'percentage')
        }),
        (_('Results'), {
            'fields': ('interpretation', 'recommendations')
        }),
        (_('Timestamp'), {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TestPurchase)
class TestPurchaseAdmin(admin.ModelAdmin):
    """Admin configuration for TestPurchase model"""
    
    list_display = ('user', 'test', 'amount_paid', 'purchased_at', 'payment_method')
    list_filter = ('payment_method', 'purchased_at', 'test__category')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'test__title', 'transaction_id')
    readonly_fields = ('purchased_at',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'test', 'amount_paid')
        }),
        (_('Payment'), {
            'fields': ('payment_method', 'transaction_id')
        }),
        (_('Timestamp'), {
            'fields': ('purchased_at',),
            'classes': ('collapse',)
        }),
    )