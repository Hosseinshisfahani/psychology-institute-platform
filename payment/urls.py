from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # Cart management
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/remove/<int:pk>/', views.CartRemoveAjaxView.as_view(), name='cart_remove'),
    path('cart/update/', views.CartUpdateAjaxView.as_view(), name='cart_update'),
    path('cart/clear/', views.CartClearAjaxView.as_view(), name='cart_clear'),
    
    # Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/success/', views.CheckoutSuccessView.as_view(), name='checkout_success'),
    path('checkout/cancel/', views.CheckoutCancelView.as_view(), name='checkout_cancel'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/invoice/', views.OrderInvoiceView.as_view(), name='order_invoice'),
    
    # Payment processing
    path('payment/<int:pk>/', views.PaymentView.as_view(), name='payment'),
    path('payment/<int:pk>/verify/', views.PaymentVerifyView.as_view(), name='payment_verify'),
    path('payment/callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),
    
    # Coupons
    path('coupon/apply/', views.CouponApplyAjaxView.as_view(), name='coupon_apply'),
    path('coupon/remove/', views.CouponRemoveView.as_view(), name='coupon_remove'),
    
    # Refunds
    path('refund/request/', views.RefundRequestView.as_view(), name='refund_request'),
    path('refunds/', views.RefundListView.as_view(), name='refund_list'),
]

