import logging

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem, Payment, PaymentMethod
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer, 
    PaymentSerializer, PaymentMethodSerializer, CreateOrderSerializer,
    ProcessPaymentSerializer
)
from .zarinpal import ZarinpalPayment


def get_frontend_url(request=None, payment=None):
    """
    Get frontend URL from various sources in priority order:
    1. Stored in payment's gateway_response (if payment provided)
    2. HTTP_REFERER header (if request provided)
    3. Request origin (if request provided and from same domain)
    4. Settings FRONTEND_URL
    5. Default localhost:3000
    """
    # Try to get from payment metadata first
    if payment and payment.gateway_response:
        if isinstance(payment.gateway_response, dict):
            # Check in data section first (where we store it)
            data_section = payment.gateway_response.get('data', {})
            if isinstance(data_section, dict):
                stored_url = data_section.get('frontend_url')
                if stored_url:
                    return stored_url
            # Also check at root level (backwards compatibility)
            stored_url = payment.gateway_response.get('frontend_url')
            if stored_url:
                return stored_url
    
    # Try to get from request referer
    if request:
        referer = request.META.get('HTTP_REFERER', '')
        if referer:
            # Extract origin from referer
            try:
                from urllib.parse import urlparse
                parsed = urlparse(referer)
                if parsed.scheme and parsed.netloc:
                    return f"{parsed.scheme}://{parsed.netloc}"
            except Exception:
                pass
        
        # Try to get from request origin header
        origin = request.META.get('HTTP_ORIGIN', '')
        if origin:
            return origin
    
    # Fall back to settings
    return getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')


class CartAPIView(APIView):
    """API view for managing shopping cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        
        # Format response for frontend
        items_data = []
        for item in cart.items.all():
            item_data = {
                'id': item.id,
                'item_type': item.item_type,
                'item_id': item.item_id,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
                'added_at': item.added_at.isoformat() if item.added_at else None
            }
            
            # Fetch full course details if item is a course
            if item.item_type == 'course':
                try:
                    from app.courses.models import Course
                    course = Course.objects.select_related('category', 'instructor').get(id=item.item_id)
                    item_data['course'] = {
                        'id': course.id,
                        'title': course.title,
                        'slug': course.slug,
                        'thumbnail': request.build_absolute_uri(course.thumbnail.url) if course.thumbnail else None,
                        'price': float(course.price) if course.price else 0,
                        'discount_price': float(course.discount_price) if course.discount_price else None,
                        'instructor_name': course.instructor.full_name if course.instructor else 'نامشخص'
                    }
                    item_data['item_title'] = course.title
                except Course.DoesNotExist:
                    # Course was deleted, skip it or mark as invalid
                    item_data['course'] = None
            elif item.item_type == 'package':
                try:
                    from app.packages.models import Package
                    package = Package.objects.select_related('category').get(id=item.item_id)
                    item_data['package'] = {
                        'id': package.id,
                        'title': package.title,
                        'slug': package.slug,
                        'thumbnail': request.build_absolute_uri(package.thumbnail.url) if package.thumbnail else None,
                        'price': float(package.price) if package.price else 0,
                        'discount_price': float(package.discount_price) if package.discount_price else None,
                        'current_price': float(package.current_price),
                        'category_name': package.category.name if package.category else None,
                        'total_courses': package.total_courses
                    }
                    item_data['item_title'] = package.title
                except Package.DoesNotExist:
                    item_data['package'] = None
                    item_data['item_title'] = f"{item.get_item_type_display()} #{item.item_id}"
            else:
                # For other item types, just add the title
                item_data['item_title'] = f"{item.get_item_type_display()} #{item.item_id}"
            
            items_data.append(item_data)
        
        return Response({
            'items': items_data,
            'total_items': cart.item_count,
            'subtotal': float(cart.total_amount),
            'discount': 0,  # TODO: Implement discount calculation
            'total': float(cart.total_amount)
        })
    
    @transaction.atomic
    def post(self, request):
        """Add item to cart"""
        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        unit_price = Decimal(str(request.data.get('unit_price', 0)))
        
        if not all([item_type, item_id, unit_price]):
            return Response(
                {'error': 'اطلاعات ناقص است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item_type=item_type,
            item_id=item_id,
            defaults={'quantity': quantity, 'unit_price': unit_price}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.unit_price = unit_price  # Update price
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    def delete(self, request, item_id=None):
        """Remove item from cart"""
        if item_id:
            cart_item = get_object_or_404(
                CartItem, 
                id=item_id, 
                cart__user=request.user
            )
            cart_item.delete()
        else:
            # Clear entire cart
            cart = get_object_or_404(Cart, user=request.user)
            cart.items.all().delete()
        
        return Response({'message': 'با موفقیت حذف شد'}, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def patch(self, request, item_id):
        """Update cart item quantity"""
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user
        )
        
        quantity = request.data.get('quantity')
        if quantity and int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            cart = cart_item.cart
            return Response({
                'item': serializer.data,
                'cart_total': float(cart.total_amount),
                'item_count': cart.item_count
            })
        else:
            return Response(
                {'error': 'تعداد باید بیشتر از صفر باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentMethodListAPIView(generics.ListAPIView):
    """List all active payment methods"""
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_payment(request):
    """Process payment and redirect to gateway"""
    serializer = ProcessPaymentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'اطلاعات ناقص است', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    payment_method = serializer.validated_data.get('payment_method')
    coupon_code = serializer.validated_data.get('coupon_code', '')
    order_id = serializer.validated_data.get('order_id')
    
    try:
        with transaction.atomic():
            # Get or create order
            if order_id:
                order = get_object_or_404(Order, id=order_id, user=request.user)
            else:
                # Create order from cart
                cart = get_object_or_404(Cart, user=request.user)
                
                if not cart.items.exists():
                    return Response(
                        {'error': 'سبد خرید شما خالی است'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculate totals
                subtotal = cart.total_amount
                discount_amount = Decimal('0')  # TODO: Calculate discount from coupon
                tax_amount = Decimal('0')  # TODO: Calculate tax if needed
                total_amount = subtotal - discount_amount + tax_amount
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    subtotal=subtotal,
                    discount_amount=discount_amount,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    payment_status='pending'
                )
                
                # Create order items from cart
                for cart_item in cart.items.all():
                    # Fetch actual item title
                    item_title = f"{cart_item.get_item_type_display()} #{cart_item.item_id}"
                    OrderItem.objects.create(
                        order=order,
                        item_type=cart_item.item_type,
                        item_id=cart_item.item_id,
                        item_title=item_title,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price,
                        total_price=cart_item.total_price
                    )
            
            # Get payment method
            if payment_method == 'zarinpal':
                # Get Zarinpal payment method
                zarinpal_method = PaymentMethod.objects.filter(
                    payment_type='zarinpal', 
                    is_active=True
                ).first()
                
                if not zarinpal_method:
                    # Create Zarinpal payment method if it doesn't exist
                    zarinpal_method = PaymentMethod.objects.create(
                        name='زرین پال',
                        payment_type='zarinpal',
                        is_active=True
                    )
                
                order.payment_method = zarinpal_method
                order.save()
                
                # Initialize Zarinpal payment
                zarinpal = ZarinpalPayment()
                
                # Reuse recent pending payment if still valid
                existing_payment = order.payments.filter(
                    payment_method=zarinpal_method,
                    status='pending'
                ).order_by('-created_at').first()
                
                if existing_payment and existing_payment.gateway_transaction_id:
                    if not zarinpal.is_authority_expired(existing_payment):
                        payment_url = zarinpal.extract_payment_url(existing_payment)
                        expires_at = zarinpal.extract_payment_expiry(existing_payment)
                        return Response({
                            'success': True,
                            'payment_url': payment_url,
                            'authority': existing_payment.gateway_transaction_id,
                            'order_id': order.id,
                            'payment_id': existing_payment.id,
                            'expires_at': expires_at,
                            'existing_payment': True
                        })
                    else:
                        zarinpal.mark_payment_expired(existing_payment)
                
                # Get frontend URL from request
                frontend_url = get_frontend_url(request=request)
                
                payment_result = zarinpal.create_payment_request(
                    order, 
                    f"پرداخت سفارش {order.order_number}",
                    frontend_url=frontend_url
                )
                
                if payment_result['success']:
                    # Clear cart if not using existing order
                    if not order_id and 'cart' in locals():
                        cart.items.all().delete()
                    
                    return Response({
                        'success': True,
                        'payment_url': payment_result['payment_url'],
                        'authority': payment_result['authority'],
                        'order_id': order.id,
                        'payment_id': payment_result['payment_id'],
                        'expires_at': payment_result.get('expires_at'),
                        'existing_payment': False
                    })
                else:
                    return Response(
                        {'error': payment_result.get('error', 'خطا در ایجاد درخواست پرداخت')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'error': f'روش پرداخت {payment_method} پشتیبانی نمی‌شود'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
    except Exception as e:
        return Response(
            {'error': f'خطا در پردازش پرداخت: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_coupon(request):
    """Apply coupon code to cart"""
    coupon_code = request.data.get('code', '').strip()
    
    if not coupon_code:
        return Response(
            {'error': 'لطفاً کد تخفیف را وارد کنید'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # TODO: Implement actual coupon validation
    # For now, simulate a simple validation
    if coupon_code.upper() == 'WELCOME10':
        discount_amount = 10000  # 10,000 Toman discount
        return Response({
            'success': True,
            'message': f'کد تخفیف با موفقیت اعمال شد. تخفیف: {discount_amount:,} تومان',
            'discount_amount': discount_amount
        })
    else:
        return Response(
            {'error': 'کد تخفیف نامعتبر است'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow any to handle Zarinpal callback
def payment_verify(request):
    """Verify payment after callback from gateway"""
    from django.shortcuts import redirect
    
    authority = request.GET.get('Authority')
    status_param = request.GET.get('Status')
    
    # Determine if this is an API call (from frontend) or a browser redirect (from Zarinpal)
    is_api_call = request.headers.get('Accept', '').startswith('application/json') or \
                  request.GET.get('format') == 'json'
    
    if status_param != 'OK' or not authority:
        if is_api_call:
            return Response(
                {'success': False, 'error': 'پرداخت ناموفق بود یا لغو شد'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Redirect to frontend with error
            frontend_url = get_frontend_url(request=request)
            return redirect(f'{frontend_url}/payment/cancel?error=payment_cancelled')
    
    try:
        # Find payment - we need to allow unauthenticated access since Zarinpal redirects here
        payment = Payment.objects.filter(
            gateway_transaction_id=authority
        ).select_related('order', 'order__user').first()
        
        if not payment:
            if is_api_call:
                return Response(
                    {'success': False, 'error': 'پرداخت یافت نشد'},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                frontend_url = get_frontend_url(request=request, payment=payment)
                return redirect(f'{frontend_url}/payment/cancel?error=payment_not_found')
        
        # Verify payment with Zarinpal
        zarinpal = ZarinpalPayment()
        verify_result = zarinpal.verify_payment(authority, payment.amount)
        
        if verify_result['success']:
            # Update payment and order status
            payment.status = 'completed'
            # Preserve registration_id if it exists
            registration_id = payment.gateway_response.get('registration_id')
            payment.gateway_response.update(verify_result)
            if registration_id:
                payment.gateway_response['registration_id'] = registration_id
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update order
            payment.order.status = 'paid'
            payment.order.payment_status = 'completed'
            payment.order.paid_at = timezone.now()
            payment.order.transaction_id = verify_result.get('ref_id', '')
            payment.order.save()

            appointment_ids = []
            try:
                deposit_items = payment.order.items.filter(item_type='appointment_deposit')
                if deposit_items.exists():
                    from app.appointments.models import Appointment

                    appointment_ids = list(deposit_items.values_list('item_id', flat=True))
                    appointments = Appointment.objects.filter(id__in=appointment_ids)

                    for appointment in appointments:
                        appointment.mark_deposit_paid(payment=payment)
            except Exception as e:  # pragma: no cover - safeguard to avoid breaking payment flow
                logger = logging.getLogger(__name__)
                logger.error(f'Error marking appointment deposit as paid: {e}')
            
            # Activate workshop registration if this order is for a workshop
            registration_id = None
            try:
                from app.workshops.models import WorkshopRegistration, InstallmentPayment
                from decimal import Decimal
                
                # Check if order has workshop items
                workshop_order_items = payment.order.items.filter(item_type='workshop')
                if workshop_order_items.exists():
                    # Find registration by order
                    # Registration ID might be stored in payment gateway_response
                    registration_id = payment.gateway_response.get('registration_id')
                    
                    if registration_id:
                        registration = WorkshopRegistration.objects.get(id=registration_id)
                    else:
                        # Fallback: find by workshop ID from order item
                        workshop_id = workshop_order_items.first().item_id
                        registration = WorkshopRegistration.objects.filter(
                            user=payment.order.user,
                            workshop_id=workshop_id,
                            status='pending_payment'
                        ).first()
                    
                    if registration:
                        registration_id = registration.id  # Update for redirect check
                        # Update registration amount_paid
                        registration.amount_paid += Decimal(str(payment.amount))
                        
                        # Handle installment payment if applicable
                        if registration.payment_type == 'installment' and hasattr(registration, 'installment_plan'):
                            # Find and mark first unpaid installment as paid
                            first_installment = registration.installment_plan.payments.filter(
                                status='pending'
                            ).order_by('installment_number').first()
                            
                            if first_installment:
                                first_installment.status = 'paid'
                                first_installment.paid_at = timezone.now()
                                first_installment.transaction_id = verify_result.get('ref_id', '')
                                first_installment.order = payment.order
                                first_installment.save()
                        
                        # Activate registration if full payment is made
                        if registration.payment_type == 'full_payment' and registration.amount_paid >= registration.total_amount:
                            registration.status = 'active'
                        elif registration.payment_type == 'installment' and registration.amount_paid > 0:
                            # Activate registration after first installment payment
                            registration.status = 'active'
                        
                        registration.save()
            except Exception as e:
                # Log error but don't fail the payment verification
                logger = logging.getLogger(__name__)
                logger.error(f'Error activating workshop registration: {str(e)}')
            
            if is_api_call:
                response_payload = {
                    'success': True,
                    'message': 'پرداخت با موفقیت انجام شد',
                    'order_id': payment.order.id,
                    'order_number': payment.order.order_number,
                    'ref_id': verify_result.get('ref_id')
                }
                if appointment_ids:
                    response_payload['appointment_ids'] = appointment_ids
                return Response(response_payload)
            else:
                # Redirect to frontend success page - redirect to My Workshops for workshop payments
                frontend_url = get_frontend_url(request=request, payment=payment)
                if registration_id:
                    # Redirect to My Workshops page for workshop payments
                    return redirect(f'{frontend_url}/dashboard/my-workshops?payment=success')
                else:
                    query = f'order_id={payment.order.id}&ref_id={verify_result.get("ref_id", "")}'
                    if appointment_ids:
                        # Use the first appointment ID for backwards compatibility
                        query += f'&appointment_id={appointment_ids[0]}'
                    return redirect(f'{frontend_url}/payment/success?{query}')
        else:
            payment.status = 'failed'
            payment.gateway_response = verify_result
            payment.save()
            
            error_msg = verify_result.get('error', 'خطا در تایید پرداخت')
            if is_api_call:
                return Response(
                    {'success': False, 'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                frontend_url = get_frontend_url(request=request, payment=payment)
                return redirect(f'{frontend_url}/payment/cancel?error={error_msg}')
            
    except Exception as e:
        if is_api_call:
            return Response(
                {'success': False, 'error': f'خطا در پردازش پرداخت: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            frontend_url = get_frontend_url(request=request)
            return redirect(f'{frontend_url}/payment/cancel?error=server_error')


class OrderListAPIView(generics.ListAPIView):
    """List user's orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            'user', 'payment_method'
        ).prefetch_related('items', 'payments').order_by('-created_at')


class OrderDetailAPIView(generics.RetrieveAPIView):
    """Get order details"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            'user', 'payment_method'
        ).prefetch_related('items', 'payments')

