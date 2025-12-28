from django.urls import path
from . import api_views

app_name = 'payment_api'

urlpatterns = [
    # Cart management
    path('cart/', api_views.CartAPIView.as_view(), name='cart'),
    path('cart/update/<int:item_id>/', api_views.CartAPIView.as_view(), name='cart_update'),
    path('cart/remove/<int:item_id>/', api_views.CartAPIView.as_view(), name='cart_remove'),
    path('cart/clear/', api_views.CartAPIView.as_view(), name='cart_clear'),
    
    # Payment methods
    path('payment-methods/', api_views.PaymentMethodListAPIView.as_view(), name='payment_methods'),
    
    # Payment processing
    path('process/', api_views.process_payment, name='process_payment'),
    path('verify/', api_views.payment_verify, name='payment_verify'),
    path('apply-coupon/', api_views.apply_coupon, name='apply_coupon'),
    
    # Orders
    path('orders/', api_views.OrderListAPIView.as_view(), name='order_list'),
    path('orders/<int:pk>/', api_views.OrderDetailAPIView.as_view(), name='order_detail'),
    
    # Wallet
    path('wallet/balance/', api_views.WalletBalanceAPIView.as_view(), name='wallet_balance'),
    path('wallet/transactions/', api_views.WalletTransactionsAPIView.as_view(), name='wallet_transactions'),
    path('wallet/use/', api_views.use_wallet_credits, name='use_wallet_credits'),
]

