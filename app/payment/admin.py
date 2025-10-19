from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
# from psychology_institute.admin import persian_admin_site
    PaymentMethod, Cart, CartItem, Order, OrderItem, 
    Payment, InstallmentSchedule
)


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ('total_price', 'added_at')
    fields = ('item_type', 'item_id', 'quantity', 'unit_price', 'total_price', 'added_at')


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('item_type', 'item_id', 'item_title', 'quantity', 'unit_price', 'total_price')


class PaymentInline(admin.TabularInline):
    """Inline admin for payments"""
    model = Payment
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fields = ('payment_method', 'amount', 'status', 'gateway_transaction_id', 'completed_at')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentMethod model"""
    
    list_display = ('name', 'payment_type', 'is_active', 'created_at')
    list_filter = ('payment_type', 'is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'payment_type', 'is_active')
        }),
        (_('Configuration'), {
            'fields': ('config',)
        }),
        (_('Timestamp'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model"""
    
    list_display = ('user', 'item_count', 'total_amount', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'item_count')
    inlines = [CartItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        (_('Summary'), {
            'fields': ('item_count', 'total_amount')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model"""
    
    list_display = ('cart', 'item_type', 'item_id', 'quantity', 'unit_price', 'total_price', 'added_at')
    list_filter = ('item_type', 'added_at')
    search_fields = ('cart__user__first_name', 'cart__user__last_name', 'cart__user__email')
    readonly_fields = ('total_price', 'added_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    
    list_display = ('order_number', 'user', 'status', 'total_amount', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'paid_at')
    search_fields = ('order_number', 'user__first_name', 'user__last_name', 'user__email', 'transaction_id')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'paid_at')
    inlines = [OrderItemInline, PaymentInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'order_number', 'status')
        }),
        (_('Pricing'), {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        (_('Payment'), {
            'fields': ('payment_method', 'payment_status', 'transaction_id')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model"""
    
    list_display = ('order', 'item_type', 'item_title', 'quantity', 'unit_price', 'total_price')
    list_filter = ('item_type',)
    search_fields = ('order__order_number', 'item_title', 'order__user__first_name', 'order__user__last_name')
    readonly_fields = ('total_price',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model"""
    
    list_display = ('order', 'payment_method', 'amount', 'status', 'gateway_transaction_id', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at', 'completed_at')
    search_fields = ('order__order_number', 'gateway_transaction_id', 'order__user__first_name', 'order__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    
    fieldsets = (
        (None, {
            'fields': ('order', 'payment_method', 'amount', 'status')
        }),
        (_('Gateway Information'), {
            'fields': ('gateway_transaction_id', 'gateway_response')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InstallmentSchedule)
class InstallmentScheduleAdmin(admin.ModelAdmin):
    """Admin configuration for InstallmentSchedule model"""
    
    list_display = ('order', 'current_installment', 'total_installments', 'next_due_date', 'is_completed')
    list_filter = ('next_due_date', 'created_at')
    search_fields = ('order__order_number', 'order__user__first_name', 'order__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'is_completed')
    
    fieldsets = (
        (None, {
            'fields': ('order',)
        }),
        (_('Installment Details'), {
            'fields': ('total_installments', 'current_installment', 'next_due_date', 'is_completed')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
