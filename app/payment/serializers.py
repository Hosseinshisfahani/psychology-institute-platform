from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment, PaymentMethod, Wallet, WalletTransaction


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods"""
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'payment_type', 'is_active', 'description']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    
    item_title = serializers.SerializerMethodField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'item_type', 'item_id', 'quantity', 'unit_price', 'item_title', 'total_price', 'added_at']
        read_only_fields = ['added_at']
    
    def get_item_title(self, obj):
        # This should fetch the actual item title based on item_type and item_id
        # For now, return a placeholder
        return f"{obj.get_item_type_display()} #{obj.item_id}"


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_amount', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    
    class Meta:
        model = OrderItem
        fields = ['id', 'item_type', 'item_id', 'item_title', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['total_price']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'payment_method_name', 'amount', 
            'status', 'gateway_transaction_id', 'created_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'completed_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_name', 'status', 'subtotal', 
            'tax_amount', 'discount_amount', 'total_amount', 'payment_method', 
            'payment_method_name', 'payment_status', 'transaction_id', 
            'items', 'payments', 'created_at', 'paid_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'paid_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order from cart"""
    
    payment_method_id = serializers.IntegerField(required=False)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_payment_method_id(self, value):
        if value:
            try:
                payment_method = PaymentMethod.objects.get(id=value, is_active=True)
                return value
            except PaymentMethod.DoesNotExist:
                raise serializers.ValidationError("روش پرداخت انتخاب شده معتبر نیست")
        return value


class ProcessPaymentSerializer(serializers.Serializer):
    """Serializer for processing payment"""
    
    payment_method = serializers.CharField(required=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    order_id = serializers.IntegerField(required=False)
    use_wallet = serializers.BooleanField(default=False, required=False)


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for wallet balance"""
    
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for wallet transactions"""
    
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount', 
            'balance_after', 'reference_id', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

