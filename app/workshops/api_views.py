from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (
    Workshop, WorkshopCategory, WorkshopSession, WorkshopRegistration,
    WorkshopSessionAttendance, InstallmentPlan, InstallmentPayment, WorkshopReview
)
from .serializers import (
    WorkshopListSerializer, WorkshopDetailSerializer, WorkshopCategorySerializer,
    WorkshopRegistrationSerializer, WorkshopSessionSerializer,
    WorkshopSessionAttendanceSerializer, InstallmentPaymentSerializer, WorkshopReviewSerializer
)
from .services.croom_service import croom_service
from app.payment.models import Cart, CartItem, Order
from dateutil.relativedelta import relativedelta


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
    if timezone.now() > workshop.registration_deadline:
        return Response(
            {'error': 'مهلت ثبت‌نام به پایان رسیده است'},
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
    
    with transaction.atomic():
        # Create registration
        registration = WorkshopRegistration.objects.create(
            user=request.user,
            workshop=workshop,
            payment_type=payment_type,
            total_amount=workshop.current_price,
            status='pending_payment'
        )
        
        # Create installment plan if installment payment
        if payment_type == 'installment':
            plan = InstallmentPlan.objects.create(
                registration=registration,
                total_amount=workshop.current_price,
                number_of_installments=workshop.installment_months,
                installment_amount=workshop.installment_amount
            )
            
            # Create installment payment records
            due_date = timezone.now().date()
            for i in range(1, workshop.installment_months + 1):
                InstallmentPayment.objects.create(
                    plan=plan,
                    installment_number=i,
                    amount=workshop.installment_amount,
                    due_date=due_date + relativedelta(months=i-1),
                    status='pending'
                )
    
    serializer = WorkshopRegistrationSerializer(registration)
    return Response({
        'message': 'ثبت‌نام شما با موفقیت انجام شد. لطفاً برای تکمیل ثبت‌نام، پرداخت را انجام دهید.',
        'registration': serializer.data
    }, status=status.HTTP_201_CREATED)


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
            {'error': 'لطفاً ابتدا پرداخت را تکمیل کنید'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get or create attendance record
    attendance, created = WorkshopSessionAttendance.objects.get_or_create(
        registration=registration,
        session=session
    )
    
    # Get personalized meeting link
    meeting_link = session.meeting_link
    if meeting_link and request.user:
        personalized_link = croom_service.get_meeting_link(
            session.meeting_id,
            {'name': request.user.full_name, 'email': request.user.email}
        )
        if personalized_link:
            meeting_link = personalized_link
    
    return Response({
        'session': WorkshopSessionSerializer(session).data,
        'meeting_link': meeting_link,
        'recording_url': session.recording_url,
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
        
        return Response({
            'plan': {
                'total_amount': float(plan.total_amount),
                'number_of_installments': plan.number_of_installments,
                'installment_amount': float(plan.installment_amount),
                'total_paid': float(plan.total_paid),
                'remaining_amount': float(plan.remaining_amount),
                'is_fully_paid': plan.is_fully_paid
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

