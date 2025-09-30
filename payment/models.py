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
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name=_('Payment Type'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    config = models.JSONField(default=dict, verbose_name=_('Configuration'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Cart(models.Model):
    """Shopping cart for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name=_('User'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
    
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
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('Cart'))
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, verbose_name=_('Item Type'))
    item_id = models.PositiveIntegerField(verbose_name=_('Item ID'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Unit Price'))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Added At'))
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('User'))
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_('Order Number'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Subtotal'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Tax Amount'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Discount Amount'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount'))
    
    # Payment
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Payment Method'))
    payment_status = models.CharField(max_length=20, default='pending', verbose_name=_('Payment Status'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Transaction ID'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Paid At'))
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
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
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('Order'))
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, verbose_name=_('Item Type'))
    item_id = models.PositiveIntegerField(verbose_name=_('Item ID'))
    item_title = models.CharField(max_length=200, verbose_name=_('Item Title'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Unit Price'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Price'))
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
    
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
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Order'))
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name=_('Payment Method'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Gateway specific fields
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Gateway Transaction ID'))
    gateway_response = models.JSONField(default=dict, verbose_name=_('Gateway Response'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number} - {self.amount}"