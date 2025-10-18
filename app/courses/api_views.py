from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import Course, Lesson, Enrollment, LessonProgress, Coupon, CoursePurchase
from .serializers import CourseDetailSerializer, LessonProgressSerializer, EnrollmentSerializer
from app.payment.models import Cart, CartItem

class CourseLearnAPIView(generics.RetrieveAPIView):
    """
    API view for course learning interface
    """
    queryset = Course.objects.filter(status='published')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_object(self):
        course = super().get_object()
        # Check if user is enrolled
        if not Enrollment.objects.filter(user=self.request.user, course=course).exists():
            raise PermissionError("شما در این دوره ثبت‌نام نکرده‌اید")
        return course

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_lesson_complete(request, lesson_id):
    """
    Mark a lesson as completed
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(user=request.user, course=lesson.course).exists():
        return Response(
            {'error': 'شما در این دوره ثبت‌نام نکرده‌اید'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    with transaction.atomic():
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'is_completed': True}
        )
        
        if not created and not progress.is_completed:
            progress.is_completed = True
            progress.save()
        
        # Check if all lessons are completed to mark course as completed
        total_lessons = lesson.course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__course=lesson.course,
            is_completed=True
        ).count()
        
        if total_lessons == completed_lessons:
            enrollment = Enrollment.objects.get(user=request.user, course=lesson.course)
            enrollment.is_completed = True
            enrollment.save()
    
    serializer = LessonProgressSerializer(progress)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_watch_time(request, lesson_id):
    """
    Update lesson watch time
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    watch_time = request.data.get('watch_time', 0)
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(user=request.user, course=lesson.course).exists():
        return Response(
            {'error': 'شما در این دوره ثبت‌نام نکرده‌اید'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'watch_time': watch_time}
    )
    
    if not created:
        progress.watch_time = max(progress.watch_time, watch_time)
        progress.save()
    
    serializer = LessonProgressSerializer(progress)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_course(request, course_slug):
    """
    Enroll user in a course
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        message = 'با موفقیت در دوره ثبت‌نام شدید'
        status_code = status.HTTP_201_CREATED
    else:
        message = 'شما قبلاً در این دوره ثبت‌نام کرده‌اید'
        status_code = status.HTTP_200_OK
    
    serializer = EnrollmentSerializer(enrollment)
    return Response({
        'message': message,
        'enrollment': serializer.data
    }, status=status_code)

class UserCoursesAPIView(generics.ListAPIView):
    """
    List user's enrolled courses
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related('course')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request, course_slug):
    """
    Add course to shopping cart
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    
    # Check if user already purchased this course
    if CoursePurchase.objects.filter(user=request.user, course=course).exists():
        return Response(
            {'error': 'شما قبلاً این دوره را خریداری کرده‌اید'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user is already enrolled (for free courses)
    if course.is_free and Enrollment.objects.filter(user=request.user, course=course).exists():
        return Response(
            {'error': 'شما قبلاً در این دوره ثبت‌نام کرده‌اید'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if item already in cart
    if CartItem.objects.filter(cart=cart, item_type='course', item_id=course.id).exists():
        return Response(
            {'error': 'این دوره قبلاً در سبد خرید شما موجود است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Add to cart
    CartItem.objects.create(
        cart=cart,
        item_type='course',
        item_id=course.id,
        unit_price=course.current_price,
        quantity=1
    )
    
    return Response({
        'message': 'دوره با موفقیت به سبد خرید اضافه شد',
        'cart_total': float(cart.total_amount)
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    """
    Validate coupon code
    """
    coupon_code = request.data.get('coupon_code', '').strip().upper()
    
    if not coupon_code:
        return Response(
            {'error': 'کد تخفیف الزامی است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        return Response(
            {'error': 'کد تخفیف نامعتبر است'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not coupon.is_valid():
        return Response(
            {'error': 'کد تخفیف منقضی شده یا غیرفعال است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get cart total for discount calculation
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_total = cart.total_amount
    
    discount_amount = coupon.calculate_discount(cart_total)
    
    return Response({
        'valid': True,
        'coupon': {
            'code': coupon.code,
            'title': coupon.title,
            'type': coupon.coupon_type,
            'discount_value': float(coupon.discount_value),
            'discount_amount': float(discount_amount),
            'min_order_amount': float(coupon.min_order_amount)
        },
        'cart_total': float(cart_total),
        'discounted_total': float(cart_total - discount_amount)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_purchases(request):
    """
    List user's course purchases
    """
    purchases = CoursePurchase.objects.filter(user=request.user).select_related('course')
    
    data = []
    for purchase in purchases:
        data.append({
            'id': purchase.id,
            'course': {
                'id': purchase.course.id,
                'title': purchase.course.title,
                'slug': purchase.course.slug,
                'thumbnail': purchase.course.thumbnail.url if purchase.course.thumbnail else None
            },
            'amount_paid': float(purchase.amount_paid),
            'original_price': float(purchase.original_price),
            'discount_amount': float(purchase.discount_amount),
            'purchased_at': purchase.purchased_at,
            'transaction_id': purchase.transaction_id
        })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def purchase_course(request, course_slug):
    """
    Purchase a course directly (bypass cart)
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    
    # Check if user already purchased this course
    if CoursePurchase.objects.filter(user=request.user, course=course).exists():
        return Response(
            {'error': 'شما قبلاً این دوره را خریداری کرده‌اید'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # For free courses, just enroll
    if course.is_free:
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if created:
            return Response({
                'message': 'با موفقیت در دوره رایگان ثبت‌نام شدید',
                'enrollment': True
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'شما قبلاً در این دوره ثبت‌نام کرده‌اید',
                'enrollment': True
            }, status=status.HTTP_200_OK)
    
    # For paid courses, add to cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Remove existing cart item if any
    CartItem.objects.filter(cart=cart, item_type='course', item_id=course.id).delete()
    
    # Add to cart
    CartItem.objects.create(
        cart=cart,
        item_type='course',
        item_id=course.id,
        unit_price=course.current_price,
        quantity=1
    )
    
    return Response({
        'message': 'دوره به سبد خرید اضافه شد. لطفاً برای تکمیل خرید به سبد خرید مراجعه کنید.',
        'cart_url': '/payment/cart/'
    }, status=status.HTTP_201_CREATED)
