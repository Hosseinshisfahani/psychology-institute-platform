from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from .models import Institution, ServicePackage, InstitutionSubscription, InstitutionOrder, InstitutionPayment, InstitutionUser


class SalesDashboardView(ListView):
    """Sales dashboard view"""
    model = Institution
    template_name = 'sales/dashboard.html'
    context_object_name = 'institutions'
    paginate_by = 10


class InstitutionListView(ListView):
    """Institution list view"""
    model = Institution
    template_name = 'sales/institution_list.html'
    context_object_name = 'institutions'
    paginate_by = 20


class InstitutionDetailView(DetailView):
    """Institution detail view"""
    model = Institution
    template_name = 'sales/institution_detail.html'
    context_object_name = 'institution'


class InstitutionCreateView(CreateView):
    """Create institution view"""
    model = Institution
    fields = ['name', 'institution_type', 'contact_person', 'email', 'phone', 'address', 'city', 'website', 'description']
    template_name = 'sales/institution_create.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'موسسه با موفقیت ایجاد شد.')
        return response


class InstitutionEditView(UpdateView):
    """Edit institution view"""
    model = Institution
    fields = ['name', 'institution_type', 'contact_person', 'email', 'phone', 'address', 'city', 'website', 'description', 'is_verified']
    template_name = 'sales/institution_edit.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'اطلاعات موسسه با موفقیت به‌روزرسانی شد.')
        return response


class ServicePackageListView(ListView):
    """Service package list view"""
    model = ServicePackage
    template_name = 'sales/package_list.html'
    context_object_name = 'packages'
    paginate_by = 20


class ServicePackageDetailView(DetailView):
    """Service package detail view"""
    model = ServicePackage
    template_name = 'sales/package_detail.html'
    context_object_name = 'package'


class ServicePackageCreateView(CreateView):
    """Create service package view"""
    model = ServicePackage
    fields = ['name', 'package_type', 'description', 'price', 'duration_months', 'max_users', 'max_tests', 'max_courses', 'max_sessions', 'features']
    template_name = 'sales/package_create.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'بسته خدمات با موفقیت ایجاد شد.')
        return response


class ServicePackageEditView(UpdateView):
    """Edit service package view"""
    model = ServicePackage
    fields = ['name', 'package_type', 'description', 'price', 'duration_months', 'max_users', 'max_tests', 'max_courses', 'max_sessions', 'features', 'is_active']
    template_name = 'sales/package_edit.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'بسته خدمات با موفقیت به‌روزرسانی شد.')
        return response


class SubscriptionListView(ListView):
    """Subscription list view"""
    model = InstitutionSubscription
    template_name = 'sales/subscription_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 20


class SubscriptionDetailView(DetailView):
    """Subscription detail view"""
    model = InstitutionSubscription
    template_name = 'sales/subscription_detail.html'
    context_object_name = 'subscription'


class SubscriptionCreateView(CreateView):
    """Create subscription view"""
    model = InstitutionSubscription
    fields = ['institution', 'package', 'start_date', 'end_date', 'price_paid']
    template_name = 'sales/subscription_create.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'اشتراک با موفقیت ایجاد شد.')
        return response


class InstitutionOrderListView(ListView):
    """Institution order list view"""
    model = InstitutionOrder
    template_name = 'sales/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20


class InstitutionOrderDetailView(DetailView):
    """Institution order detail view"""
    model = InstitutionOrder
    template_name = 'sales/order_detail.html'
    context_object_name = 'order'


class InstitutionOrderApproveView(CreateView):
    """Approve institution order view"""
    template_name = 'sales/order_approve.html'
    
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(InstitutionOrder, pk=kwargs['pk'])
        return render(request, self.template_name, {'order': order})


class InstitutionOrderRejectView(CreateView):
    """Reject institution order view"""
    template_name = 'sales/order_reject.html'
    
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(InstitutionOrder, pk=kwargs['pk'])
        return render(request, self.template_name, {'order': order})


class InstitutionPaymentListView(ListView):
    """Institution payment list view"""
    model = InstitutionPayment
    template_name = 'sales/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20


class InstitutionPaymentDetailView(DetailView):
    """Institution payment detail view"""
    model = InstitutionPayment
    template_name = 'sales/payment_detail.html'
    context_object_name = 'payment'


class InstitutionUserListView(ListView):
    """Institution user list view"""
    model = InstitutionUser
    template_name = 'sales/institution_user_list.html'
    context_object_name = 'institution_users'
    paginate_by = 20
    
    def get_queryset(self):
        institution = get_object_or_404(Institution, pk=self.kwargs['institution_pk'])
        return InstitutionUser.objects.filter(institution=institution)


class InstitutionUserAddView(CreateView):
    """Add institution user view"""
    model = InstitutionUser
    fields = ['user', 'role']
    template_name = 'sales/institution_user_add.html'
    
    def form_valid(self, form):
        institution = get_object_or_404(Institution, pk=self.kwargs['institution_pk'])
        form.instance.institution = institution
        response = super().form_valid(form)
        messages.success(self.request, 'کاربر با موفقیت به موسسه اضافه شد.')
        return response


class InstitutionUserEditView(UpdateView):
    """Edit institution user view"""
    model = InstitutionUser
    fields = ['role', 'is_active']
    template_name = 'sales/institution_user_edit.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'اطلاعات کاربر با موفقیت به‌روزرسانی شد.')
        return response