from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from .models import PsychologicalTest, TestCategory, TestSession, TestResult, Question, Answer


class TestListView(ListView):
    """List view for psychological tests"""
    model = PsychologicalTest
    template_name = 'tests/test_list.html'
    context_object_name = 'tests'
    paginate_by = 12
    
    def get_queryset(self):
        return PsychologicalTest.objects.filter(is_active=True).select_related('category', 'created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = TestCategory.objects.filter(is_active=True)
        context['featured_tests'] = PsychologicalTest.objects.filter(
            is_active=True
        ).select_related('category', 'created_by')[:6]
        context['total_tests'] = PsychologicalTest.objects.filter(is_active=True).count()
        context['free_tests_count'] = PsychologicalTest.objects.filter(
            is_active=True, is_free=True
        ).count()
        context['popular_tests'] = PsychologicalTest.objects.filter(
            is_active=True
        ).select_related('category', 'created_by')[:5]
        return context


class TestCategoryView(ListView):
    """List view for tests in a specific category"""
    model = PsychologicalTest
    template_name = 'tests/test_category.html'
    context_object_name = 'tests'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(TestCategory, slug=self.kwargs['slug'])
        return PsychologicalTest.objects.filter(
            is_active=True,
            category=self.category
        ).select_related('category', 'created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = TestCategory.objects.filter(is_active=True)
        return context


class TestDetailView(DetailView):
    """Detail view for individual tests"""
    model = PsychologicalTest
    template_name = 'tests/test_detail.html'
    context_object_name = 'test'
    
    def get_queryset(self):
        return PsychologicalTest.objects.filter(is_active=True).select_related('category', 'created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test = self.get_object()
        
        # Get related tests
        context['related_tests'] = PsychologicalTest.objects.filter(
            is_active=True,
            category=test.category
        ).exclude(id=test.id).select_related('category', 'created_by')[:3]
        
        # Get user's test result if exists
        if self.request.user.is_authenticated:
            try:
                context['user_test_result'] = TestResult.objects.get(
                    session__user=self.request.user,
                    session__test=test
                )
            except TestResult.DoesNotExist:
                context['user_test_result'] = None
        else:
            context['user_test_result'] = None
            
        return context


class TestPurchaseView(CreateView):
    """View for purchasing tests"""
    template_name = 'tests/test_purchase.html'
    
    def get(self, request, *args, **kwargs):
        test = get_object_or_404(PsychologicalTest, pk=kwargs['pk'])
        return render(request, self.template_name, {'test': test})


class TestSessionView(DetailView):
    """View for test sessions"""
    model = TestSession
    template_name = 'tests/test_session.html'
    context_object_name = 'session'


class TestSessionStartView(CreateView):
    """View for starting a test session"""
    model = TestSession
    fields = []
    template_name = 'tests/test_session_start.html'
    
    def form_valid(self, form):
        test = get_object_or_404(PsychologicalTest, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.test = test
        response = super().form_valid(form)
        return response


class TestQuestionView(LoginRequiredMixin, DetailView):
    """View for test questions"""
    model = TestSession
    template_name = 'tests/test_session.html'
    context_object_name = 'session'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        question = get_object_or_404(Question, pk=self.kwargs['question_pk'])
        
        # Get all questions for this test
        all_questions = session.test.questions.all().order_by('order')
        current_index = list(all_questions).index(question)
        
        context['question'] = question
        context['current_question_number'] = current_index + 1
        context['total_questions'] = all_questions.count()
        context['progress_percentage'] = (current_index / all_questions.count()) * 100
        
        # Navigation
        context['has_previous'] = current_index > 0
        context['has_next'] = current_index < all_questions.count() - 1
        
        if context['has_previous']:
            context['previous_question'] = all_questions[current_index - 1]
        if context['has_next']:
            context['next_question'] = all_questions[current_index + 1]
            
        return context
    
    def post(self, request, *args, **kwargs):
        session = self.get_object()
        question = get_object_or_404(Question, pk=self.kwargs['question_pk'])
        
        # Save the answer
        answer, created = Answer.objects.get_or_create(
            session=session,
            question=question
        )
        
        # Update answer based on question type
        if question.question_type == 'single_choice':
            choice_id = request.POST.get('choice')
            if choice_id:
                answer.selected_choices.clear()
                answer.selected_choices.add(choice_id)
        elif question.question_type == 'multiple_choice':
            choice_ids = request.POST.getlist('choices')
            answer.selected_choices.clear()
            for choice_id in choice_ids:
                answer.selected_choices.add(choice_id)
        elif question.question_type == 'text':
            answer.text_answer = request.POST.get('text_answer', '')
        elif question.question_type == 'number':
            answer.number_answer = request.POST.get('number_answer')
            
        answer.save()
        
        # Navigate to next question or finish test
        all_questions = session.test.questions.all().order_by('order')
        current_index = list(all_questions).index(question)
        
        if current_index < all_questions.count() - 1:
            next_question = all_questions[current_index + 1]
            return redirect('tests:test_question', session.pk, next_question.pk)
        else:
            # Test completed
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()
            return redirect('tests:test_session_submit', session.pk)


class TestSessionSubmitView(CreateView):
    """View for submitting test sessions"""
    template_name = 'tests/test_submit.html'
    
    def get(self, request, *args, **kwargs):
        session = get_object_or_404(TestSession, pk=kwargs['pk'])
        return render(request, self.template_name, {'session': session})


class TestResultView(DetailView):
    """View for test results"""
    model = TestResult
    template_name = 'tests/test_result.html'
    context_object_name = 'result'


class UserTestResultsView(ListView):
    """View for user's test results"""
    model = TestResult
    template_name = 'tests/user_results.html'
    context_object_name = 'results'
    paginate_by = 10
    
    def get_queryset(self):
        return TestResult.objects.filter(
            session__user=self.request.user
        ).select_related('session__test')


class FreeTestListView(ListView):
    """List view for free tests"""
    model = PsychologicalTest
    template_name = 'tests/free_test_list.html'
    context_object_name = 'tests'
    paginate_by = 12
    
    def get_queryset(self):
        return PsychologicalTest.objects.filter(
            is_active=True,
            is_free=True
        ).select_related('category', 'created_by')