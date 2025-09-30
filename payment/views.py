from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from .models import Cart, CartItem, Order, Payment, PaymentMethod
from .forms import CartItemForm, CheckoutForm


class CartView(LoginRequiredMixin, ListView):
    """Shopping cart view"""
    model = CartItem
    template_name = 'payment/cart.html'
    context_object_name = 'cart_items'
    
    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        return context


class CartAddView(CreateView):
    """Add item to cart view"""
    model = CartItem
    fields = ['item_type', 'item_id', 'quantity', 'unit_price']
    template_name = 'payment/cart_add.html'
    
    def form_valid(self, form):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        form.instance.cart = cart
        response = super().form_valid(form)
        return response


class CartRemoveView(CreateView):
    """Remove item from cart view"""
    template_name = 'payment/cart_remove.html'
    
    def get(self, request, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, pk=kwargs['pk'])
        return render(request, self.template_name, {'cart_item': cart_item})


class CartUpdateView(CreateView):
    """Update cart view"""
    template_name = 'payment/cart_update.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CartClearView(CreateView):
    """Clear cart view"""
    template_name = 'payment/cart_clear.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CheckoutView(CreateView):
    """Checkout view"""
    model = Order
    fields = ['payment_method']
    template_name = 'payment/checkout.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        return response


class CheckoutSuccessView(DetailView):
    """Checkout success view"""
    model = Order
    template_name = 'payment/checkout_success.html'
    context_object_name = 'order'


class CheckoutCancelView(CreateView):
    """Checkout cancel view"""
    template_name = 'payment/checkout_cancel.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class OrderListView(ListView):
    """User orders list view"""
    model = Order
    template_name = 'payment/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(DetailView):
    """Order detail view"""
    model = Order
    template_name = 'payment/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderInvoiceView(DetailView):
    """Order invoice view"""
    model = Order
    template_name = 'payment/order_invoice.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class PaymentView(DetailView):
    """Payment view"""
    model = Payment
    template_name = 'payment/payment.html'
    context_object_name = 'payment'


class PaymentVerifyView(CreateView):
    """Payment verification view"""
    template_name = 'payment/payment_verify.html'
    
    def get(self, request, *args, **kwargs):
        payment = get_object_or_404(Payment, pk=kwargs['pk'])
        return render(request, self.template_name, {'payment': payment})


class PaymentCallbackView(CreateView):
    """Payment callback view"""
    template_name = 'payment/payment_callback.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CouponApplyView(CreateView):
    """Apply coupon view"""
    template_name = 'payment/coupon_apply.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CouponRemoveView(CreateView):
    """Remove coupon view"""
    template_name = 'payment/coupon_remove.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class RefundRequestView(CreateView):
    """Refund request view"""
    template_name = 'payment/refund_request.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class RefundListView(ListView):
    """Refund list view"""
    model = Order
    template_name = 'payment/refund_list.html'
    context_object_name = 'refunds'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# AJAX Views for Cart Operations
@method_decorator(csrf_exempt, name='dispatch')
class CartUpdateAjaxView(LoginRequiredMixin, TemplateView):
    """AJAX view for updating cart item quantity"""
    
    def post(self, request, *args, **kwargs):
        try:
            import json
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 1))
            
            if quantity < 1:
                return JsonResponse({'success': False, 'message': 'تعداد باید بیشتر از صفر باشد'})
            
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'تعداد با موفقیت به‌روزرسانی شد',
                'total_price': float(cart_item.total_price),
                'cart_total': float(cart_item.cart.total_amount)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'خطا در به‌روزرسانی'})
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'message': 'Method not allowed'})


@method_decorator(csrf_exempt, name='dispatch')
class CartRemoveAjaxView(LoginRequiredMixin, TemplateView):
    """AJAX view for removing cart item"""
    
    def post(self, request, *args, **kwargs):
        try:
            item_id = kwargs.get('pk')
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart = cart_item.cart
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'آیتم با موفقیت حذف شد',
                'cart_total': float(cart.total_amount),
                'item_count': cart.item_count
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'خطا در حذف آیتم'})
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'message': 'Method not allowed'})


@method_decorator(csrf_exempt, name='dispatch')
class CartClearAjaxView(LoginRequiredMixin, TemplateView):
    """AJAX view for clearing cart"""
    
    def post(self, request, *args, **kwargs):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.items.all().delete()
            
            return JsonResponse({
                'success': True,
                'message': 'سبد خرید با موفقیت پاک شد'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'خطا در پاک کردن سبد خرید'})
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'message': 'Method not allowed'})


@method_decorator(csrf_exempt, name='dispatch')
class CouponApplyAjaxView(LoginRequiredMixin, TemplateView):
    """AJAX view for applying coupon codes"""
    
    def post(self, request, *args, **kwargs):
        try:
            import json
            data = json.loads(request.body)
            coupon_code = data.get('coupon_code', '').strip()
            
            if not coupon_code:
                return JsonResponse({'success': False, 'message': 'لطفاً کد تخفیف را وارد کنید'})
            
            # Here you would implement actual coupon validation logic
            # For now, we'll simulate a simple validation
            if coupon_code.upper() == 'WELCOME10':
                discount_amount = 10000  # 10,000 Toman discount
                return JsonResponse({
                    'success': True,
                    'message': f'کد تخفیف با موفقیت اعمال شد. تخفیف: {discount_amount:,} تومان',
                    'discount_amount': discount_amount
                })
            else:
                return JsonResponse({'success': False, 'message': 'کد تخفیف نامعتبر است'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'خطا در اعمال کد تخفیف'})
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'message': 'Method not allowed'})