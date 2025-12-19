import logging
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from .models import (
    Workshop, WorkshopCategory, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview,
    WorkshopCertificate
)
from .serializers import (
    WorkshopListSerializer, WorkshopDetailSerializer, WorkshopCategorySerializer,
    WorkshopRegistrationSerializer, WorkshopSessionSerializer,
    WorkshopSessionAttendanceSerializer, InstallmentPaymentSerializer, WorkshopReviewSerializer,
    WorkshopCertificateSerializer
)
from .services.croom_service import croom_service
from .services.certificate_service import certificate_service
from app.payment.models import Cart, CartItem, Order, OrderItem, Payment, PaymentMethod
from app.payment.zarinpal import ZarinpalPayment
from app.payment.api_views import get_frontend_url
from dateutil.relativedelta import relativedelta


logger = logging.getLogger(__name__)

class WorkshopListAPIView(generics.ListAPIView):
    """List all published workshops"""
    serializer_class = WorkshopListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Workshop.objects.filter(status__in=['published', 'registration_open'])
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by payment type
        payment_type = self.request.query_params.get('payment_type')
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        return queryset.select_related('category', 'instructor').order_by('-created_at')


class WorkshopDetailAPIView(generics.RetrieveAPIView):
    """Get workshop detail"""
    queryset = Workshop.objects.all()
    serializer_class = WorkshopDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class WorkshopCategoryListAPIView(generics.ListAPIView):
    """List all workshop categories"""
    queryset = WorkshopCategory.objects.filter(is_active=True)
    serializer_class = WorkshopCategorySerializer
    permission_classes = [permissions.AllowAny]


class UserWorkshopsAPIView(generics.ListAPIView):
    """List user's registered workshops"""
    serializer_class = WorkshopRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkshopRegistration.objects.filter(
            user=self.request.user
        ).select_related('workshop', 'installment_plan').prefetch_related(
            'installment_plan__payments'
        ).order_by('-registered_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_workshop(request, workshop_slug):
    """Register for a workshop"""
    try:
        workshop = get_object_or_404(Workshop, slug=workshop_slug)
        
        # Check if workshop is open for registration
        if workshop.status not in ['registration_open', 'published']:
            return Response(
                {'error': 'ثبت‌نام برای این کارگاه باز نیست'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if workshop is full
        if workshop.is_full:
            return Response(
                {'error': 'ظرفیت کارگاه تکمیل شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if registration deadline has passed
        now = timezone.now()
        deadline = workshop.registration_deadline
        
        if not deadline:
            return Response(
                {'error': 'مهلت ثبت‌نام تعریف نشده است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # CRITICAL FIX: Check if deadline is stored as Persian (Jalali) date
        import jdatetime
        deadline_utc = deadline
        
        if hasattr(deadline, 'year') and 1300 <= deadline.year <= 1500:
            # Deadline is stored in Persian calendar format - convert to Gregorian
            try:
                hour = deadline.hour if hasattr(deadline, 'hour') else 0
                minute = deadline.minute if hasattr(deadline, 'minute') else 0
                second = deadline.second if hasattr(deadline, 'second') else 0
                
                jdt = jdatetime.datetime(
                    deadline.year,
                    deadline.month,
                    deadline.day,
                    hour,
                    minute,
                    second
                )
                gregorian_dt = jdt.togregorian()
                
                gregorian_datetime = datetime(
                    gregorian_dt.year,
                    gregorian_dt.month,
                    gregorian_dt.day,
                    hour,
                    minute,
                    second
                )
                
                if timezone.is_aware(deadline):
                    deadline_tz = deadline.tzinfo
                    deadline_utc = timezone.make_aware(gregorian_datetime, deadline_tz)
                    if deadline_tz != timezone.utc:
                        deadline_utc = deadline_utc.astimezone(timezone.utc)
                else:
                    from django.conf import settings
                    import pytz
                    local_tz = pytz.timezone(settings.TIME_ZONE)
                    deadline_local = local_tz.localize(gregorian_datetime)
                    deadline_utc = deadline_local.astimezone(timezone.utc)
            except Exception:
                if timezone.is_naive(deadline):
                    from django.conf import settings
                    import pytz
                    local_tz = pytz.timezone(settings.TIME_ZONE)
                    deadline_utc = local_tz.localize(deadline).astimezone(timezone.utc)
                else:
                    deadline_utc = deadline.astimezone(timezone.utc) if deadline.tzinfo != timezone.utc else deadline
        else:
            if timezone.is_naive(deadline):
                from django.conf import settings
                import pytz
                local_tz = pytz.timezone(settings.TIME_ZONE)
                deadline_utc = local_tz.localize(deadline).astimezone(timezone.utc)
            else:
                deadline_utc = deadline.astimezone(timezone.utc) if deadline.tzinfo != timezone.utc else deadline
        
        # Compare in UTC
        if now > deadline_utc:
            try:
                deadline_persian = jdatetime.datetime.fromgregorian(datetime=deadline_utc).strftime('%Y/%m/%d - %H:%M')
                now_persian = jdatetime.datetime.fromgregorian(datetime=now).strftime('%Y/%m/%d - %H:%M')
            except Exception:
                deadline_persian = str(deadline_utc)
                now_persian = str(now)
            
            return Response(
                {
                    'error': 'مهلت ثبت‌نام به پایان رسیده است',
                    'debug': {
                        'now_utc': str(now),
                        'deadline_utc': str(deadline_utc),
                        'original_deadline': str(deadline),
                        'now_persian': now_persian,
                        'deadline_persian': deadline_persian,
                        'difference_days': (deadline_utc - now).days if deadline_utc > now else (now - deadline_utc).days
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already registered
        if WorkshopRegistration.objects.filter(user=request.user, workshop=workshop).exists():
            return Response(
                {'error': 'شما قبلاً در این کارگاه ثبت‌نام کرده‌اید'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_type = request.data.get('payment_type', 'full_payment')
        
        # Validate payment type
        if workshop.payment_type == 'full_payment' and payment_type == 'installment':
            return Response(
                {'error': 'این کارگاه فقط پرداخت کامل را قبول می‌کند'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if workshop.payment_type == 'installment' and payment_type == 'full_payment':
            return Response(
                {'error': 'این کارگاه فقط پرداخت قسطی را قبول می‌کند'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already in cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        existing_cart_item = CartItem.objects.filter(
            cart=cart,
            item_type='workshop',
            item_id=workshop.id
        ).first()
        
        if existing_cart_item:
            # Update payment type if different
            if existing_cart_item.metadata.get('payment_type') != payment_type:
                existing_cart_item.metadata['payment_type'] = payment_type
                # Update price based on payment type
                if payment_type == 'installment':
                    existing_cart_item.unit_price = workshop.installment_amount
                else:
                    existing_cart_item.unit_price = workshop.current_price
                existing_cart_item.save()
            
            return Response({
                'success': True,
                'message': 'این کارگاه در سبد خرید شما موجود است. لطفاً به سبد خرید بروید.',
                'redirect_url': '/payment/cart'
            }, status=status.HTTP_200_OK)
        
        # Calculate payment amount based on payment type
        if payment_type == 'installment':
            payment_amount = Decimal(str(workshop.installment_amount))
        else:
            payment_amount = Decimal(str(workshop.current_price))
        
        # Add workshop to cart with payment type metadata
        cart_item = CartItem.objects.create(
            cart=cart,
            item_type='workshop',
            item_id=workshop.id,
            unit_price=payment_amount,
            quantity=1,
            metadata={
                'workshop_slug': workshop.slug,
                'payment_type': payment_type,
                'workshop_price': str(workshop.current_price),
                'installment_amount': str(workshop.installment_amount) if payment_type == 'installment' else None,
                'installment_months': workshop.installment_months if payment_type == 'installment' else None,
            }
        )
        
        return Response({
            'success': True,
            'message': 'کارگاه به سبد خرید اضافه شد. لطفاً به سبد خرید بروید و پرداخت را تکمیل کنید.',
            'cart_item_id': cart_item.id,
            'payment_type': payment_type,
            'payment_amount': str(payment_amount),
            'workshop': {
                'id': workshop.id,
                'title': workshop.title,
                'slug': workshop.slug,
            },
            'redirect_url': '/payment/cart'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.exception(f"[Workshop Register] Unexpected error registering workshop '{workshop_slug}': {e}")
        return Response(
            {'error': 'خطا در ثبت‌نام. لطفاً با پشتیبانی تماس بگیرید.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_workshop_order(request, order_number):
    """Get workshop order details for checkout page"""
    try:
        order = Order.objects.get(
            order_number=order_number,
            user=request.user
        )
    except Order.DoesNotExist:
        return Response(
            {'error': 'سفارش یافت نشد یا دسترسی به آن ممکن نیست'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    order_items = []
    workshop_details = None
    
    for item in order.items.all():
        order_items.append({
            'id': item.id,
            'item_type': item.item_type,
            'item_id': item.item_id,
            'item_title': item.item_title,
            'quantity': item.quantity,
            'unit_price': str(item.unit_price),
            'total_price': str(item.total_price),
        })
        
        if item.item_type == 'workshop':
            try:
                workshop = Workshop.objects.get(id=item.item_id)
                workshop_details = {
                    'id': workshop.id,
                    'title': workshop.title,
                    'slug': workshop.slug,
                    'price': str(workshop.current_price),
                    'thumbnail': workshop.thumbnail.url if workshop.thumbnail else None,
                    'instructor_name': workshop.instructor_name,
                    'payment_type': workshop.payment_type,
                }
            except Workshop.DoesNotExist:
                pass
    
    return Response({
        'id': order.id,
        'order_number': order.order_number,
        'subtotal': str(order.subtotal),
        'discount_amount': str(order.discount_amount),
        'tax_amount': str(order.tax_amount),
        'total_amount': str(order.total_amount),
        'payment_status': order.payment_status,
        'created_at': order.created_at,
        'items': order_items,
        'workshop_details': workshop_details,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_workshop_order_payment(request, order_number):
    """Process payment for a workshop order"""
    try:
        order = Order.objects.get(
            order_number=order_number,
            user=request.user
        )
    except Order.DoesNotExist:
        return Response(
            {'error': 'سفارش یافت نشد یا دسترسی به آن ممکن نیست'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if order.payment_status == 'completed':
        return Response(
            {'error': 'این سفارش قبلاً پرداخت شده است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    zarinpal_method = PaymentMethod.objects.filter(
        payment_type='zarinpal',
        is_active=True
    ).first()
    
    if not zarinpal_method:
        zarinpal_method = PaymentMethod.objects.create(
            name='زرین پال',
            payment_type='zarinpal',
            is_active=True
        )
    
    order.payment_method = zarinpal_method
    order.save()
    
    zarinpal = ZarinpalPayment()
    order_item = order.items.first()
    workshop_title = order_item.item_title if order_item else 'کارگاه'
    
    frontend_url = get_frontend_url(request=request)

    payment_result = zarinpal.create_payment_request(
        order,
        f"پرداخت {workshop_title}",
        frontend_url=frontend_url
    )
    
    if not payment_result['success']:
        error_details = payment_result.get('details', {})
        logger.error(
            f'Zarinpal payment request failed for order {order.id}: '
            f"{payment_result.get('error')} - Details: {error_details}"
        )
        return Response(
            {
                'success': False,
                'error': payment_result.get('error', 'خطا در ایجاد درخواست پرداخت'),
                'details': error_details if error_details else None
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        workshop_item = order.items.filter(item_type='workshop').first()
        if workshop_item:
            registration = WorkshopRegistration.objects.filter(
                user=request.user,
                workshop_id=workshop_item.item_id,
                status='pending_payment'
            ).first()
            
            if registration:
                payment = Payment.objects.get(id=payment_result['payment_id'])
                if payment.gateway_response is None:
                    payment.gateway_response = {}
                payment.gateway_response['registration_id'] = registration.id
                payment.save()
    except Exception as e:
        logger.error(f'Error storing registration_id in payment: {str(e)}')
    
    return Response({
        'success': True,
        'payment_url': payment_result['payment_url'],
        'authority': payment_result['authority'],
        'payment_id': payment_result['payment_id']
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_workshop_to_cart(request, workshop_slug):
    """Add workshop to cart"""
    workshop = get_object_or_404(Workshop, slug=workshop_slug)
    
    # Check if already registered
    if WorkshopRegistration.objects.filter(user=request.user, workshop=workshop).exists():
        return Response(
            {'error': 'شما قبلاً در این کارگاه ثبت‌نام کرده‌اید'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if already in cart
    if CartItem.objects.filter(cart=cart, item_type='workshop', item_id=workshop.id).exists():
        return Response(
            {'error': 'این کارگاه در سبد خرید شما موجود است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    CartItem.objects.create(
        cart=cart,
        item_type='workshop',
        item_id=workshop.id,
        unit_price=workshop.current_price,
        quantity=1
    )
    
    return Response({
        'message': 'کارگاه به سبد خرید اضافه شد',
        'cart_total': float(cart.total_amount)
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def workshop_session_access(request, session_id):
    """Get workshop session access details including meeting link"""
    session = get_object_or_404(WorkshopSession, id=session_id)
    workshop = session.workshop
    
    # Check if user is registered
    try:
        registration = WorkshopRegistration.objects.get(user=request.user, workshop=workshop)
    except WorkshopRegistration.DoesNotExist:
        return Response(
            {'error': 'شما در این کارگاه ثبت‌نام نکرده‌اید'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if payment is completed (at least first installment)
    if registration.status == 'pending_payment':
        return Response(
            {
                'error': 'لطفاً ابتدا پرداخت را تکمیل کنید',
                'banner': {
                    'type': 'warning',
                    'message': 'برای دسترسی به جلسات، ابتدا پرداخت خود را تکمیل کنید.'
                }
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Restrict access if there is any overdue installment
    try:
        plan = registration.installment_plan
        overdue_exists = plan.payments.filter(status='pending', due_date__lt=timezone.now().date()).exists()
        if overdue_exists:
            # Optionally mark registration as suspended
            if registration.status != 'suspended':
                registration.status = 'suspended'
                registration.save(update_fields=['status'])
            return Response(
                {
                    'error': 'به علت عدم پرداخت قسط سررسید شده، دسترسی شما محدود شده است',
                    'banner': {
                        'type': 'error',
                        'message': 'قسط بعدی شما سررسید شده است. تا زمان تسویه، دسترسی به محتوا محدود است.'
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
    except WorkshopRegistration.installment_plan.RelatedObjectDoesNotExist:
        pass
    
    # Get or create attendance record
    attendance, created = WorkshopSessionAttendance.objects.get_or_create(
        registration=registration,
        session=session
    )
    
    # Get meeting link from croom_platform_link
    meeting_link = session.croom_platform_link
    
    # Note: If personalized meeting links are needed, meeting_id should be stored in the model
    # or extracted from the croom_platform_link URL. For now, we use the platform link directly.
    
    # Get recording URL from session_video if available
    recording_url = None
    if session.session_video:
        recording_url = session.session_video.url
    
    return Response({
        'session': WorkshopSessionSerializer(session).data,
        'meeting_link': meeting_link,
        'recording_url': recording_url,
        'can_join': session.scheduled_datetime and (
            session.scheduled_datetime - timezone.timedelta(minutes=15) <= timezone.now()
        ),
        'attendance': WorkshopSessionAttendanceSerializer(attendance).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_session_attendance(request, session_id):
    """Mark attendance for a session"""
    session = get_object_or_404(WorkshopSession, id=session_id)
    
    try:
        registration = WorkshopRegistration.objects.get(
            user=request.user, 
            workshop=session.workshop
        )
    except WorkshopRegistration.DoesNotExist:
        return Response(
            {'error': 'شما در این کارگاه ثبت‌نام نکرده‌اید'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    attendance, created = WorkshopSessionAttendance.objects.get_or_create(
        registration=registration,
        session=session
    )
    
    attendance.attended = True
    attendance.attendance_marked_at = timezone.now()
    if not attendance.join_time:
        attendance.join_time = timezone.now()
    attendance.save()
    
    # Update registration progress
    registration.update_progress()
    
    serializer = WorkshopSessionAttendanceSerializer(attendance)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def workshop_installments(request, workshop_slug):
    """Get installment payment schedule for a workshop"""
    workshop = get_object_or_404(Workshop, slug=workshop_slug)
    
    try:
        registration = WorkshopRegistration.objects.get(user=request.user, workshop=workshop)
        if not hasattr(registration, 'installment_plan'):
            return Response(
                {'error': 'این کارگاه با پرداخت قسطی ثبت‌نام نشده است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan = registration.installment_plan
        payments = plan.payments.all().order_by('installment_number')

        # Determine next pending payment
        next_payment = payments.filter(status='pending').order_by('due_date', 'installment_number').first()
        has_overdue = payments.filter(status='pending', due_date__lt=timezone.now().date()).exists()
        next_payment_data = InstallmentPaymentSerializer(next_payment).data if next_payment else None
        
        return Response({
            'plan': {
                'total_amount': float(plan.total_amount),
                'number_of_installments': plan.number_of_installments,
                'installment_amount': float(plan.installment_amount),
                'total_paid': float(plan.total_paid),
                'remaining_amount': float(plan.remaining_amount),
                'is_fully_paid': plan.is_fully_paid,
                'has_overdue': has_overdue,
                'next_payment': next_payment_data
            },
            'payments': InstallmentPaymentSerializer(payments, many=True).data
        })
        
    except WorkshopRegistration.DoesNotExist:
        return Response(
            {'error': 'شما در این کارگاه ثبت‌نام نکرده‌اید'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_workshop_review(request, workshop_slug):
    """Create a review for a workshop"""
    workshop = get_object_or_404(Workshop, slug=workshop_slug)
    
    try:
        registration = WorkshopRegistration.objects.get(user=request.user, workshop=workshop)
    except WorkshopRegistration.DoesNotExist:
        return Response(
            {'error': 'فقط شرکت‌کنندگان کارگاه می‌توانند نظر بدهند'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if already reviewed
    if hasattr(registration, 'review'):
        return Response(
            {'error': 'شما قبلاً برای این کارگاه نظر داده‌اید'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = WorkshopReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(registration=registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_workshop_payment(request, workshop_slug):
    """Complete payment for an existing workshop registration"""
    workshop = get_object_or_404(Workshop, slug=workshop_slug)
    
    # Check if user has a registration
    try:
        registration = WorkshopRegistration.objects.get(
            user=request.user,
            workshop=workshop,
            status='pending_payment'
        )
    except WorkshopRegistration.DoesNotExist:
        return Response(
            {'error': 'شما در این کارگاه ثبت‌نام نکرده‌اید یا پرداخت شما تکمیل شده است'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Find existing unpaid order for this registration
    # Look for orders with workshop items that match this workshop
    unpaid_order = Order.objects.filter(
        user=request.user,
        payment_status='pending',
        items__item_type='workshop',
        items__item_id=workshop.id
    ).order_by('-created_at').first()
    
    # If no order exists, create a new one
    with transaction.atomic():
        if not unpaid_order:
            # Calculate payment amount
            if registration.payment_type == 'installment':
                # Find first unpaid installment
                if hasattr(registration, 'installment_plan'):
                    first_unpaid = registration.installment_plan.payments.filter(
                        status='pending'
                    ).order_by('installment_number').first()
                    if first_unpaid:
                        payment_amount = first_unpaid.amount
                    else:
                        return Response(
                            {'error': 'همه اقساط پرداخت شده است'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        {'error': 'خطا در یافتن اطلاعات اقساط'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Full payment - calculate remaining amount
                payment_amount = registration.total_amount - registration.amount_paid
            
            # Create new order
            unpaid_order = Order.objects.create(
                user=request.user,
                subtotal=payment_amount,
                discount_amount=Decimal('0'),
                tax_amount=Decimal('0'),
                total_amount=payment_amount,
                payment_status='pending'
            )
            
            # Create order item
            OrderItem.objects.create(
                order=unpaid_order,
                item_type='workshop',
                item_id=workshop.id,
                item_title=workshop.title,
                quantity=1,
                unit_price=payment_amount,
            total_price=payment_amount,
            metadata={
                'workshop_slug': workshop.slug,
                'payment_type': registration.payment_type,
            }
            )
        else:
            # Use existing unpaid order - ensure it's refreshed from DB
            unpaid_order.refresh_from_db()
    
    # Get or create Zarinpal payment method
    zarinpal_method = PaymentMethod.objects.filter(
        payment_type='zarinpal',
        is_active=True
    ).first()
    
    if not zarinpal_method:
        zarinpal_method = PaymentMethod.objects.create(
            name='زرین پال',
            payment_type='zarinpal',
            is_active=True
        )
    
    unpaid_order.payment_method = zarinpal_method
    unpaid_order.save()
    
    # Create payment request
    zarinpal = ZarinpalPayment()
    frontend_url = get_frontend_url(request=request)
    payment_result = zarinpal.create_payment_request(
        unpaid_order,
        f"پرداخت کارگاه {workshop.title}",
        frontend_url=frontend_url
    )
    
    if not payment_result['success']:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f'Zarinpal payment request failed for order {unpaid_order.id}: '
            f"{payment_result.get('error')}"
        )
        
        return Response(
            {
                'error': payment_result.get('error', 'خطا در ایجاد درخواست پرداخت'),
                'details': payment_result.get('details')
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Store registration_id in payment metadata
    try:
        payment = Payment.objects.get(id=payment_result['payment_id'])
        if payment.gateway_response is None:
            payment.gateway_response = {}
        payment.gateway_response['registration_id'] = registration.id
        payment.save()
    except Payment.DoesNotExist:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Payment with ID {payment_result.get("payment_id")} not found after creation')
    
    return Response({
        'message': 'در حال انتقال به درگاه پرداخت...',
        'payment_url': payment_result['payment_url'],
        'authority': payment_result['authority'],
        'order_id': unpaid_order.id,
        'payment_id': payment_result['payment_id']
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def workshop_reviews(request, workshop_slug):
    """Get approved reviews for a workshop"""
    workshop = get_object_or_404(Workshop, slug=workshop_slug)
    reviews = WorkshopReview.objects.filter(
        registration__workshop=workshop,
        is_approved=True
    ).order_by('-created_at')
    
    serializer = WorkshopReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_certificate(request, workshop_slug):
    """Generate a certificate for a completed workshop"""
    workshop = get_object_or_404(Workshop, slug=workshop_slug)
    
    try:
        registration = WorkshopRegistration.objects.get(
            user=request.user,
            workshop=workshop
        )
    except WorkshopRegistration.DoesNotExist:
        return Response(
            {'error': 'شما در این کارگاه ثبت‌نام نکرده‌اید'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if certificate can be issued
    can_issue, reason = certificate_service.can_issue_certificate(registration)
    if not can_issue:
        return Response(
            {'error': reason},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create certificate
    certificate, created = WorkshopCertificate.objects.get_or_create(
        registration=registration,
        defaults={
            'status': 'pending',
            'issued_by': request.user if request.user.is_staff else None
        }
    )
    
    # Generate and save certificate PDF
    if certificate_service.generate_and_save_certificate(certificate):
        serializer = WorkshopCertificateSerializer(certificate, context={'request': request})
        return Response({
            'message': 'گواهینامه با موفقیت صادر شد',
            'certificate': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'خطا در تولید گواهینامه'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_certificate(request, workshop_slug):
    """Get certificate for a workshop"""
    workshop = get_object_or_404(Workshop, slug=workshop_slug)
    
    try:
        registration = WorkshopRegistration.objects.get(
            user=request.user,
            workshop=workshop
        )
    except WorkshopRegistration.DoesNotExist:
        return Response(
            {'error': 'شما در این کارگاه ثبت‌نام نکرده‌اید'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        certificate = registration.certificate
        serializer = WorkshopCertificateSerializer(certificate, context={'request': request})
        return Response(serializer.data)
    except WorkshopCertificate.DoesNotExist:
        return Response(
            {'error': 'گواهینامه برای این کارگاه صادر نشده است'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_certificate(request, certificate_id):
    """Download certificate PDF file"""
    certificate = get_object_or_404(WorkshopCertificate, id=certificate_id)
    
    # Check if user owns this certificate or is staff
    if certificate.registration.user != request.user and not request.user.is_staff:
        return Response(
            {'error': 'شما اجازه دسترسی به این گواهینامه را ندارید'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if not certificate.certificate_file:
        # Try to generate if not exists
        if certificate_service.generate_and_save_certificate(certificate):
            certificate.refresh_from_db()
        else:
            return Response(
                {'error': 'فایل گواهینامه موجود نیست و امکان تولید آن وجود ندارد'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    from django.http import FileResponse
    return FileResponse(
        certificate.certificate_file.open('rb'),
        content_type='application/pdf',
        filename=f"certificate_{certificate.certificate_number}.pdf"
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_certificates(request):
    """Get all certificates for the authenticated user"""
    certificates = WorkshopCertificate.objects.filter(
        registration__user=request.user,
        status='issued'
    ).select_related(
        'registration__workshop',
        'registration__workshop__instructor'
    ).order_by('-issued_at', '-created_at')
    
    serializer = WorkshopCertificateSerializer(certificates, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_certificate(request, verification_code):
    """Verify a certificate by verification code (public endpoint)"""
    try:
        certificate = WorkshopCertificate.objects.get(verification_code=verification_code)
    except WorkshopCertificate.DoesNotExist:
        return Response(
            {'error': 'گواهینامه یافت نشد'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = WorkshopCertificateSerializer(certificate, context={'request': request})
    return Response({
        'valid': certificate.is_valid,
        'certificate': serializer.data
    })

