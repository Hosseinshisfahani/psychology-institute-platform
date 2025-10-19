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
    
    name = models.CharField(max_length=200, verbose_name='نام')
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES, verbose_name='نوع موسسه')
    contact_person = models.CharField(max_length=100, verbose_name='شخص تماس')
    email = models.EmailField(verbose_name='ایمیل')
    phone = models.CharField(max_length=20, verbose_name='تلفن')
    address = models.TextField(verbose_name='آدرس')
    city = models.CharField(max_length=100, verbose_name='شهر')
    website = models.URLField(blank=True, null=True, verbose_name='وب‌سایت')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    is_verified = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('موسسه')
        verbose_name_plural = _('موسسات')
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
    
    name = models.CharField(max_length=200, verbose_name='نام')
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, verbose_name='نوع پکیج')
    description = models.TextField(verbose_name='توضیحات')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    duration_months = models.PositiveIntegerField(verbose_name='مدت ماه')
    
    # Package features
    max_users = models.PositiveIntegerField(verbose_name='حداکثر کاربران')
    max_tests = models.PositiveIntegerField(verbose_name='حداکثر تست‌ها')
    max_courses = models.PositiveIntegerField(verbose_name='حداکثر دوره‌ها')
    max_sessions = models.PositiveIntegerField(verbose_name='حداکثر جلسات')
    
    # Features included
    features = models.JSONField(default=list, verbose_name='ویژگی‌ها')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('پکیج خدمات')
        verbose_name_plural = _('پکیج‌های خدمات')
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
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='موسسه')
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='پکیج')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='وضعیت')
    
    # Subscription details
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت پرداخت شده')
    
    # Usage tracking
    current_users = models.PositiveIntegerField(default=0, verbose_name='کاربران فعلی')
    tests_used = models.PositiveIntegerField(default=0, verbose_name='تست‌های استفاده شده')
    courses_used = models.PositiveIntegerField(default=0, verbose_name='دوره‌های استفاده شده')
    sessions_used = models.PositiveIntegerField(default=0, verbose_name='جلسات استفاده شده')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('اشتراک موسسه')
        verbose_name_plural = _('اشتراک‌های موسسه')
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
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='institution_users', verbose_name='موسسه')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='institution_memberships', verbose_name='کاربر')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name='نقش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')
    
    class Meta:
        verbose_name = _('کاربر موسسه')
        verbose_name_plural = _('کاربران موسسه')
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
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='orders', verbose_name='موسسه')
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='orders', verbose_name='پکیج')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # Order details
    quantity = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت واحد')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ کل')
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_orders', verbose_name='تأیید شده توسط')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تأیید')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('سفارش موسسه')
        verbose_name_plural = _('سفارشات موسسه')
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
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='payments', verbose_name='موسسه')
    order = models.ForeignKey(InstitutionOrder, on_delete=models.CASCADE, related_name='payments', verbose_name='سفارش')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    payment_method = models.CharField(max_length=50, verbose_name='روش پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    
    class Meta:
        verbose_name = _('پرداخت موسسه')
        verbose_name_plural = _('پرداخت‌های موسسه')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment from {self.institution.name} - {self.amount}"