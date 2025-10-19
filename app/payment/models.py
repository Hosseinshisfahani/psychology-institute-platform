from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

User = get_user_model()


class PaymentMethod(models.Model):
    """Available payment methods"""
    
    PAYMENT_TYPES = [
        ('zarinpal', _('ZarinPal')),
        ('bank_transfer', _('Bank Transfer')),
        ('credit_card', _('Credit Card')),
        ('wallet', _('Wallet')),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name='نوع پرداخت')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    config = models.JSONField(default=dict, verbose_name='پیکربندی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('روش پرداخت')
        verbose_name_plural = _('روش‌های پرداخت')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Cart(models.Model):
    """Shopping cart for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='کاربر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')
    
    def __str__(self):
        return f"Cart for {self.user.full_name}"
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    """Items in shopping cart"""
    
    ITEM_TYPES = [
        ('course', _('Course')),
        ('test', _('Test')),
        ('session', _('Session')),
        ('package', _('Package')),
        ('workshop', _('Workshop')),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='سبد خرید')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, verbose_name='نوع آیتم')
    item_id = models.PositiveIntegerField(verbose_name='شناسه آیتم')
    quantity = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت واحد')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ اضافه شدن')
    
    class Meta:
        verbose_name = _('آیتم سبد خرید')
        verbose_name_plural = _('آیتم‌های سبد خرید')
        unique_together = ['cart', 'item_type', 'item_id']
    
    def __str__(self):
        return f"{self.get_item_type_display()} #{self.item_id} in {self.cart.user.full_name}'s cart"
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Order(models.Model):
    """Orders placed by users"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('paid', _('Paid')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')
    order_number = models.CharField(max_length=50, unique=True, verbose_name='شماره سفارش')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='جمع کل')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ مالیات')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ تخفیف')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ کل')
    
    # Payment
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='روش پرداخت')
    payment_status = models.CharField(max_length=20, default='pending', verbose_name='وضعیت پرداخت')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ پرداخت')
    
    class Meta:
        verbose_name = _('سفارش')
        verbose_name_plural = _('سفارشات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Items in an order"""
    
    ITEM_TYPES = [
        ('course', _('Course')),
        ('test', _('Test')),
        ('session', _('Session')),
        ('package', _('Package')),
        ('workshop', _('Workshop')),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='سفارش')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, verbose_name='نوع آیتم')
    item_id = models.PositiveIntegerField(verbose_name='شناسه آیتم')
    item_title = models.CharField(max_length=200, verbose_name='عنوان آیتم')
    quantity = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت واحد')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت کل')
    
    class Meta:
        verbose_name = _('آیتم سفارش')
        verbose_name_plural = _('آیتم‌های سفارش')
    
    def __str__(self):
        return f"{self.item_title} in Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='سفارش')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name='روش پرداخت')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # Gateway specific fields
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه تراکنش درگاه')
    gateway_response = models.JSONField(default=dict, verbose_name='پاسخ درگاه')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    
    class Meta:
        verbose_name = _('پرداخت')
        verbose_name_plural = _('پرداخت‌ها')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number} - {self.amount}"


class InstallmentSchedule(models.Model):
    """Installment schedule for orders"""
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='installment_schedule', verbose_name='سفارش')
    total_installments = models.PositiveIntegerField(verbose_name='تعداد کل اقساط')
    current_installment = models.PositiveIntegerField(default=0, verbose_name='قسط فعلی')
    next_due_date = models.DateField(blank=True, null=True, verbose_name='تاریخ سررسید بعدی')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('برنامه اقساط')
        verbose_name_plural = _('برنامه‌های اقساط')
    
    def __str__(self):
        return f"Installment Schedule for {self.order.order_number}"
    
    @property
    def is_completed(self):
        """Check if all installments are paid"""
        return self.current_installment >= self.total_installments