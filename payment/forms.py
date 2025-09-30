from django import forms
from .models import CartItem, Order, PaymentMethod


class CartItemForm(forms.ModelForm):
    """Form for adding items to cart"""
    
    class Meta:
        model = CartItem
        fields = ['item_type', 'item_id', 'quantity', 'unit_price']
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'item_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_type'].label = 'نوع آیتم'
        self.fields['item_id'].label = 'شناسه آیتم'
        self.fields['quantity'].label = 'تعداد'
        self.fields['unit_price'].label = 'قیمت واحد'


class CheckoutForm(forms.ModelForm):
    """Form for checkout process"""
    
    class Meta:
        model = Order
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].label = 'روش پرداخت'
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(is_active=True)


class CouponForm(forms.Form):
    """Form for applying coupon codes"""
    
    coupon_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تخفیف را وارد کنید'
        }),
        label='کد تخفیف'
    )


class RefundRequestForm(forms.Form):
    """Form for requesting refunds"""
    
    REASON_CHOICES = [
        ('technical_issue', 'مشکل فنی'),
        ('not_satisfied', 'عدم رضایت از محتوا'),
        ('duplicate_purchase', 'خرید تکراری'),
        ('wrong_item', 'خرید اشتباه'),
        ('other', 'سایر موارد'),
    ]
    
    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='دلیل درخواست بازگشت وجه'
    )
    
    explanation = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'توضیحات بیشتر در مورد دلیل درخواست بازگشت وجه...'
        }),
        label='توضیحات',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].label = 'دلیل درخواست بازگشت وجه'
        self.fields['explanation'].label = 'توضیحات'
