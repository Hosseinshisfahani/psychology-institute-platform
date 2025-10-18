from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.db import models
from .models import Session, SessionType, TherapistAvailability, SessionRating, SessionCancellation
from .forms import SessionBookingForm, SessionRescheduleForm

User = get_user_model()


class SessionListView(LoginRequiredMixin, ListView):
    """List view for therapy sessions"""
    model = Session
    template_name = 'therapy_sessions/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 10
    
    def get_queryset(self):
        return Session.objects.filter(client=self.request.user).order_by('-scheduled_date', '-scheduled_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get session statistics
        all_sessions = Session.objects.filter(client=user)
        context['upcoming_sessions'] = all_sessions.filter(
            status__in=['scheduled', 'confirmed'],
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date', 'scheduled_time')
        
        context['completed_sessions'] = all_sessions.filter(status='completed').order_by('-scheduled_date')
        context['cancelled_sessions'] = all_sessions.filter(status='cancelled').order_by('-scheduled_date')
        
        # Statistics
        context['upcoming_sessions_count'] = context['upcoming_sessions'].count()
        context['completed_sessions_count'] = context['completed_sessions'].count()
        context['available_therapists_count'] = User.objects.filter(user_type='therapist', is_active=True, is_available=True).count()
        
        # Calculate total hours
        total_minutes = all_sessions.filter(status='completed').aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0
        context['total_hours'] = round(total_minutes / 60, 1)
        
        return context


class SessionBookingView(LoginRequiredMixin, CreateView):
    """View for booking therapy sessions"""
    model = Session
    form_class = SessionBookingForm
    template_name = 'therapy_sessions/session_booking.html'
    
    def form_valid(self, form):
        form.instance.client = self.request.user
        form.instance.price = form.instance.session_type.price
        form.instance.duration_minutes = form.instance.session_type.duration_minutes
        
        # Generate meeting link for online sessions
        if form.instance.mode == 'online':
            form.instance.meeting_link = f"https://meet.example.com/{form.instance.id}"
            form.instance.meeting_id = f"MEET{form.instance.id:06d}"
            form.instance.meeting_password = "123456"  # In real app, generate secure password
        
        messages.success(self.request, 'جلسه شما با موفقیت رزرو شد.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('therapy_sessions:session_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['therapists'] = User.objects.filter(user_type='therapist', is_active=True, is_available=True)
        context['session_types'] = SessionType.objects.filter(is_active=True)
        return context


class TherapistListView(ListView):
    """List view for therapists"""
    model = User
    template_name = 'therapy_sessions/therapist_list.html'
    context_object_name = 'therapists'
    paginate_by = 12
    
    def get_queryset(self):
        return User.objects.filter(user_type='therapist', is_active=True).order_by('first_name', 'last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        therapists = User.objects.filter(user_type='therapist', is_active=True)
        
        context['total_therapists'] = therapists.count()
        context['available_therapists'] = therapists.filter(is_available=True).count()
        
        # Calculate average experience
        total_experience = therapists.aggregate(total=models.Sum('experience_years'))['total'] or 0
        context['average_experience'] = round(total_experience / context['total_therapists'], 1) if context['total_therapists'] > 0 else 0
        
        # Calculate average rate
        total_rate = therapists.aggregate(total=models.Avg('hourly_rate'))['total'] or 0
        context['average_rate'] = int(total_rate) if total_rate else 0
        
        return context


class TherapistDetailView(DetailView):
    """Detail view for individual therapists"""
    model = User
    template_name = 'therapy_sessions/therapist_detail.html'
    context_object_name = 'therapist'
    
    def get_queryset(self):
        return User.objects.filter(user_type='therapist', is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        therapist = self.get_object()
        
        # Get session types offered by this therapist
        context['session_types'] = SessionType.objects.filter(is_active=True)
        
        # Get ratings for this therapist
        ratings = SessionRating.objects.filter(session__therapist=therapist)
        context['ratings'] = ratings
        context['total_ratings'] = ratings.count()
        
        if context['total_ratings'] > 0:
            context['average_rating'] = ratings.aggregate(avg=models.Avg('overall_rating'))['avg']
            
            # Calculate rating distribution
            rating_counts = {}
            for i in range(1, 6):
                count = ratings.filter(overall_rating=i).count()
                rating_counts[f'rating_{i}'] = round((count / context['total_ratings']) * 100, 1)
            context.update(rating_counts)
            
            context['recent_ratings'] = ratings.order_by('-created_at')[:5]
        else:
            context['average_rating'] = 0
            for i in range(1, 6):
                context[f'rating_{i}'] = 0
            context['recent_ratings'] = []
        
        return context


class TherapistAvailabilityView(DetailView):
    """View for therapist availability"""
    model = User
    template_name = 'therapy_sessions/therapist_availability.html'
    context_object_name = 'therapist'
    
    def get_queryset(self):
        return User.objects.filter(user_type='therapist', is_active=True)


class UserSessionsView(ListView):
    """View for user's sessions"""
    model = Session
    template_name = 'therapy_sessions/user_sessions.html'
    context_object_name = 'sessions'
    paginate_by = 10
    
    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)


class SessionDetailView(DetailView):
    """Detail view for individual sessions"""
    model = Session
    template_name = 'therapy_sessions/session_detail.html'
    context_object_name = 'session'


class SessionCancelView(CreateView):
    """View for cancelling sessions"""
    template_name = 'therapy_sessions/session_cancel.html'
    
    def get(self, request, *args, **kwargs):
        session = get_object_or_404(Session, pk=kwargs['pk'])
        return render(request, self.template_name, {'session': session})


class SessionRescheduleView(CreateView):
    """View for rescheduling sessions"""
    template_name = 'therapy_sessions/session_reschedule.html'
    
    def get(self, request, *args, **kwargs):
        session = get_object_or_404(Session, pk=kwargs['pk'])
        return render(request, self.template_name, {'session': session})


class SessionTypeListView(ListView):
    """List view for session types"""
    model = SessionType
    template_name = 'therapy_sessions/session_type_list.html'
    context_object_name = 'session_types'


class SessionNotesView(DetailView):
    """View for session notes"""
    model = Session
    template_name = 'therapy_sessions/session_notes.html'
    context_object_name = 'session'


class SessionNoteCreateView(CreateView):
    """View for creating session notes"""
    template_name = 'therapy_sessions/session_note_create.html'
    
    def get(self, request, *args, **kwargs):
        session = get_object_or_404(Session, pk=kwargs['pk'])
        return render(request, self.template_name, {'session': session})


class SessionRatingView(LoginRequiredMixin, CreateView):
    """View for rating sessions"""
    template_name = 'therapy_sessions/session_rating.html'
    
    def get(self, request, *args, **kwargs):
        session = get_object_or_404(Session, pk=kwargs['pk'], client=request.user)
        return render(request, self.template_name, {'session': session})
    
    def post(self, request, *args, **kwargs):
        session = get_object_or_404(Session, pk=kwargs['pk'], client=request.user)
        
        # Check if already rated
        if hasattr(session, 'rating'):
            messages.warning(request, 'شما قبلاً این جلسه را امتیاز داده‌اید.')
            return redirect('therapy_sessions:session_detail', pk=session.pk)
        
        # Create rating
        rating = SessionRating.objects.create(
            session=session,
            overall_rating=request.POST.get('overall_rating'),
            therapist_rating=request.POST.get('therapist_rating'),
            environment_rating=request.POST.get('environment_rating'),
            helpfulness_rating=request.POST.get('helpfulness_rating'),
            comments=request.POST.get('comments', ''),
            would_recommend=request.POST.get('would_recommend') == 'true'
        )
        
        messages.success(request, 'امتیاز شما با موفقیت ثبت شد.')
        return redirect('therapy_sessions:session_detail', pk=session.pk)


class TherapistDashboardView(ListView):
    """Therapist dashboard view"""
    model = Session
    template_name = 'therapy_sessions/therapist_dashboard.html'
    context_object_name = 'sessions'
    
    def get_queryset(self):
        return Session.objects.filter(therapist=self.request.user)


class TherapistSessionsView(ListView):
    """Therapist sessions view"""
    model = Session
    template_name = 'therapy_sessions/therapist_sessions.html'
    context_object_name = 'sessions'
    paginate_by = 10
    
    def get_queryset(self):
        return Session.objects.filter(therapist=self.request.user)


class TherapistAvailabilityManageView(CreateView):
    """View for managing therapist availability"""
    template_name = 'therapy_sessions/therapist_availability_manage.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)