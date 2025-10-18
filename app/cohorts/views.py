from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Cohort, CohortEnrollment


class CohortListView(ListView):
    """List view for cohorts"""
    model = Cohort
    template_name = 'cohorts/cohort_list.html'
    context_object_name = 'cohorts'
    paginate_by = 12
    
    def get_queryset(self):
        return Cohort.objects.filter(
            is_active=True,
            status__in=['upcoming', 'active']
        ).select_related('instructor').order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_cohorts'] = Cohort.objects.filter(
            is_active=True,
            status='upcoming'
        ).select_related('instructor')[:6]
        return context


class CohortDetailView(DetailView):
    """Detail view for a cohort"""
    model = Cohort
    template_name = 'cohorts/cohort_detail.html'
    context_object_name = 'cohort'
    
    def get_queryset(self):
        return Cohort.objects.filter(is_active=True).select_related('instructor').prefetch_related('sessions')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if user is enrolled
        if self.request.user.is_authenticated:
            context['is_enrolled'] = CohortEnrollment.objects.filter(
                student=self.request.user,
                cohort=self.object
            ).exists()
        else:
            context['is_enrolled'] = False
        
        return context


class CohortEnrollView(LoginRequiredMixin, CreateView):
    """Enrollment view for cohorts"""
    model = CohortEnrollment
    fields = ['payment_type']
    template_name = 'cohorts/cohort_enroll.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cohort'] = get_object_or_404(Cohort, id=self.kwargs['cohort_id'])
        return context
    
    def form_valid(self, form):
        cohort = get_object_or_404(Cohort, id=self.kwargs['cohort_id'])
        
        # Check if cohort is full
        if cohort.is_full:
            messages.error(self.request, 'این کلاس تکمیل شده است')
            return redirect('cohorts:cohort_detail', pk=cohort.id)
        
        # Check if user already enrolled
        if CohortEnrollment.objects.filter(student=self.request.user, cohort=cohort).exists():
            messages.error(self.request, 'شما قبلاً در این کلاس ثبت‌نام کرده‌اید')
            return redirect('cohorts:cohort_detail', pk=cohort.id)
        
        form.instance.student = self.request.user
        form.instance.cohort = cohort
        
        # Calculate total amount based on payment type
        payment_type = form.cleaned_data['payment_type']
        if payment_type == 'full':
            form.instance.total_amount = cohort.full_price
        elif payment_type == 'installment_3':
            form.instance.total_amount = cohort.installment_3_price or cohort.full_price
        elif payment_type == 'installment_6':
            form.instance.total_amount = cohort.installment_6_price or cohort.full_price
        
        response = super().form_valid(form)
        messages.success(self.request, 'با موفقیت در کلاس ثبت‌نام شدید')
        return response
    
    def get_success_url(self):
        return reverse_lazy('cohorts:cohort_detail', kwargs={'pk': self.kwargs['cohort_id']})


class UserCohortsView(LoginRequiredMixin, ListView):
    """User's enrolled cohorts"""
    model = CohortEnrollment
    template_name = 'cohorts/user_cohorts.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return CohortEnrollment.objects.filter(
            student=self.request.user
        ).select_related('cohort', 'cohort__instructor').order_by('-enrolled_at')
