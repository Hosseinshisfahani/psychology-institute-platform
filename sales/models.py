from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Institution(models.Model):
    """Institutions that can purchase services"""
    
    INSTITUTION_TYPES = [
        ('university', _('University')),
        ('school', _('School')),
        ('clinic', _('Clinic')),
        ('hospital', _('Hospital')),
        ('company', _('Company')),
        ('ngo', _('NGO')),
        ('government', _('Government')),
        ('other', _('Other')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES, verbose_name=_('Institution Type'))
    contact_person = models.CharField(max_length=100, verbose_name=_('Contact Person'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, verbose_name=_('Phone'))
    address = models.TextField(verbose_name=_('Address'))
    city = models.CharField(max_length=100, verbose_name=_('City'))
    website = models.URLField(blank=True, null=True, verbose_name=_('Website'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Is Verified'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Institution')
        verbose_name_plural = _('Institutions')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ServicePackage(models.Model):
    """Service packages for institutions"""
    
    PACKAGE_TYPES = [
        ('basic', _('Basic')),
        ('standard', _('Standard')),
        ('premium', _('Premium')),
        ('enterprise', _('Enterprise')),
        ('custom', _('Custom')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, verbose_name=_('Package Type'))
    description = models.TextField(verbose_name=_('Description'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    duration_months = models.PositiveIntegerField(verbose_name=_('Duration (Months)'))
    
    # Package features
    max_users = models.PositiveIntegerField(verbose_name=_('Maximum Users'))
    max_tests = models.PositiveIntegerField(verbose_name=_('Maximum Tests'))
    max_courses = models.PositiveIntegerField(verbose_name=_('Maximum Courses'))
    max_sessions = models.PositiveIntegerField(verbose_name=_('Maximum Sessions'))
    
    # Features included
    features = models.JSONField(default=list, verbose_name=_('Features'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Service Package')
        verbose_name_plural = _('Service Packages')
        ordering = ['package_type', 'price']
    
    def __str__(self):
        return f"{self.name} - {self.get_package_type_display()}"


class InstitutionSubscription(models.Model):
    """Institution subscriptions to service packages"""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('suspended', _('Suspended')),
        ('cancelled', _('Cancelled')),
    ]
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_('Institution'))
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_('Package'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_('Status'))
    
    # Subscription details
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price Paid'))
    
    # Usage tracking
    current_users = models.PositiveIntegerField(default=0, verbose_name=_('Current Users'))
    tests_used = models.PositiveIntegerField(default=0, verbose_name=_('Tests Used'))
    courses_used = models.PositiveIntegerField(default=0, verbose_name=_('Courses Used'))
    sessions_used = models.PositiveIntegerField(default=0, verbose_name=_('Sessions Used'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Institution Subscription')
        verbose_name_plural = _('Institution Subscriptions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.institution.name} - {self.package.name}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == 'active' and self.end_date >= timezone.now().date()


class InstitutionUser(models.Model):
    """Users associated with institutions"""
    
    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('manager', _('Manager')),
        ('user', _('User')),
        ('viewer', _('Viewer')),
    ]
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='institution_users', verbose_name=_('Institution'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='institution_memberships', verbose_name=_('User'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name=_('Role'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Joined At'))
    
    class Meta:
        verbose_name = _('Institution User')
        verbose_name_plural = _('Institution Users')
        unique_together = ['institution', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} at {self.institution.name}"


class InstitutionOrder(models.Model):
    """Orders placed by institutions"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Institution'))
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Package'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Order details
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Unit Price'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount'))
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_orders', verbose_name=_('Approved By'))
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Approved At'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Institution Order')
        verbose_name_plural = _('Institution Orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order for {self.institution.name} - {self.package.name}"


class InstitutionPayment(models.Model):
    """Payments from institutions"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Institution'))
    order = models.ForeignKey(InstitutionOrder, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Order'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    payment_method = models.CharField(max_length=50, verbose_name=_('Payment Method'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Transaction ID'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    
    class Meta:
        verbose_name = _('Institution Payment')
        verbose_name_plural = _('Institution Payments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment from {self.institution.name} - {self.amount}"