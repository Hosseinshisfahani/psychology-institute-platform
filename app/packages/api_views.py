from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import (
    Package, PackageCategory, PackagePurchase, PackageEnrollment,
    PackageProgress, PackageReview, PackageCoupon
)
from .serializers import (
    PackageListSerializer, PackageDetailSerializer, PackageCategorySerializer,
    PackagePurchaseSerializer, PackageEnrollmentSerializer,
    PackageProgressSerializer, PackageReviewSerializer, PackageCouponSerializer
)
from app.courses.models import Enrollment
from app.payment.models import Cart, CartItem


class PackageListAPIView(generics.ListAPIView):
    """List all published packages"""
    serializer_class = PackageListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Package.objects.filter(status='published')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.select_related('category').prefetch_related('courses').order_by('-created_at')


class PackageDetailAPIView(generics.RetrieveAPIView):
    """Get package detail"""
    queryset = Package.objects.filter(status='published')
    serializer_class = PackageDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PackageCategoryListAPIView(generics.ListAPIView):
    """List all package categories"""
    queryset = PackageCategory.objects.filter(is_active=True)
    serializer_class = PackageCategorySerializer
    permission_classes = [permissions.AllowAny]


class UserPackagesAPIView(generics.ListAPIView):
    """List user's purchased packages"""
    serializer_class = PackagePurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PackagePurchase.objects.filter(
            user=self.request.user
        ).select_related(
            'package', 'package__category', 'progress'
        ).prefetch_related(
            'course_enrollments__enrollment__course',
            'package__courses'
        ).order_by('-purchased_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def purchase_package(request, package_slug):
    """Purchase a package"""
    package = get_object_or_404(Package, slug=package_slug, status='published')
    
    # Check if already purchased
    if PackagePurchase.objects.filter(user=request.user, package=package).exists():
        return Response(
            {'error': 'شما قبلاً این بسته را خریداری کرده‌اید'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    with transaction.atomic():
        # Create purchase
        purchase = PackagePurchase.objects.create(
            user=request.user,
            package=package,
            amount_paid=package.current_price,
            original_price=package.price,
            discount_amount=package.price - package.current_price if package.discount_price else 0,
            payment_method='pending'
        )
        
        # Create course enrollments
        purchase.create_course_enrollments()
        
        # Create progress tracker
        PackageProgress.objects.create(purchase=purchase)
        
        # Increment purchase count
        package.purchase_count += 1
        package.save(update_fields=['purchase_count'])
    
    serializer = PackagePurchaseSerializer(purchase)
    return Response({
        'message': 'بسته با موفقیت خریداری شد',
        'purchase': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_package_to_cart(request, package_slug):
    """Add package to cart"""
    package = get_object_or_404(Package, slug=package_slug, status='published')
    
    # Check if already purchased
    if PackagePurchase.objects.filter(user=request.user, package=package).exists():
        return Response(
            {
                'error': 'شما قبلاً این بسته را خریداری کرده‌اید',
                'cart_url': '/payment/cart/'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        item_type='package',
        item_id=package.id,
        defaults={
            'unit_price': package.current_price,
            'quantity': 1
        }
    )
    
    if not item_created:
        cart_item.unit_price = package.current_price
        cart_item.quantity = 1
        cart_item.save(update_fields=['unit_price', 'quantity'])
    
    message = 'بسته به سبد خرید اضافه شد' if item_created else 'این بسته پیش‌تر در سبد خرید شما وجود داشت. اطلاعات آن به‌روزرسانی شد.'
    
    return Response({
        'message': message,
        'status': 'added' if item_created else 'existing',
        'cart_url': '/payment/cart/'
    }, status=status.HTTP_201_CREATED if item_created else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def package_progress(request, package_slug):
    """Get progress for a package"""
    package = get_object_or_404(Package, slug=package_slug)
    
    try:
        purchase = PackagePurchase.objects.get(user=request.user, package=package)
        
        # Get or create progress
        progress, created = PackageProgress.objects.get_or_create(purchase=purchase)
        if created or not progress.overall_progress_percentage:
            progress.calculate_progress()
        
        # Get individual course progress
        course_enrollments = purchase.course_enrollments.all()
        
        return Response({
            'overall_progress': PackageProgressSerializer(progress).data,
            'courses': PackageEnrollmentSerializer(course_enrollments, many=True).data
        })
        
    except PackagePurchase.DoesNotExist:
        return Response(
            {'error': 'شما این بسته را خریداری نکرده‌اید'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def package_courses(request, package_slug):
    """Get all courses in a package with user's access"""
    package = get_object_or_404(Package, slug=package_slug)
    
    try:
        purchase = PackagePurchase.objects.get(user=request.user, package=package)
        
        # Check if expired
        if purchase.is_expired:
            return Response(
                {'error': 'دسترسی شما به این بسته منقضی شده است'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get courses with enrollment status
        courses_data = []
        for course in package.courses.all():
            enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
            
            courses_data.append({
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'description': course.short_description,
                'duration_hours': course.duration_hours,
                'thumbnail': course.thumbnail.url if course.thumbnail else None,
                'progress_percentage': enrollment.progress_percentage if enrollment else 0,
                'is_enrolled': enrollment is not None,
                'status': enrollment.status if enrollment else None,
            })
        
        return Response({
            'package': {
                'id': package.id,
                'title': package.title,
                'total_courses': package.total_courses,
            },
            'courses': courses_data,
            'purchase': {
                'purchased_at': purchase.purchased_at,
                'expires_at': purchase.expires_at,
                'is_expired': purchase.is_expired,
            }
        })
        
    except PackagePurchase.DoesNotExist:
        return Response(
            {'error': 'شما این بسته را خریداری نکرده‌اید'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_package_review(request, package_slug):
    """Create a review for a package"""
    package = get_object_or_404(Package, slug=package_slug)
    
    try:
        purchase = PackagePurchase.objects.get(user=request.user, package=package)
    except PackagePurchase.DoesNotExist:
        return Response(
            {'error': 'فقط خریداران بسته می‌توانند نظر بدهند'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if already reviewed
    if hasattr(purchase, 'review'):
        return Response(
            {'error': 'شما قبلاً برای این بسته نظر داده‌اید'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = PackageReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(purchase=purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def package_reviews(request, package_slug):
    """Get approved reviews for a package"""
    package = get_object_or_404(Package, slug=package_slug)
    reviews = PackageReview.objects.filter(
        purchase__package=package,
        is_approved=True
    ).order_by('-created_at')
    
    serializer = PackageReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_package_coupon(request, package_slug):
    """Validate coupon code for a package"""
    package = get_object_or_404(Package, slug=package_slug, status='published')
    coupon_code = request.data.get('coupon_code', '').strip().upper()
    
    if not coupon_code:
        return Response(
            {'error': 'کد تخفیف الزامی است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        coupon = PackageCoupon.objects.get(code=coupon_code)
    except PackageCoupon.DoesNotExist:
        return Response(
            {'error': 'کد تخفیف نامعتبر است'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not coupon.is_valid():
        return Response(
            {'error': 'کد تخفیف منقضی شده یا غیرفعال است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if coupon is applicable to this package
    if coupon.applicable_packages.exists() and package not in coupon.applicable_packages.all():
        return Response(
            {'error': 'این کد تخفیف برای این بسته معتبر نیست'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    discount_amount = coupon.calculate_discount(package.current_price)
    
    return Response({
        'valid': True,
        'coupon': PackageCouponSerializer(coupon).data,
        'discount_amount': float(discount_amount),
        'original_price': float(package.current_price),
        'final_price': float(package.current_price - discount_amount)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_package_enrollments(request):
    """Get all user's package enrollments"""
    purchases = PackagePurchase.objects.filter(user=request.user)
    
    data = []
    for purchase in purchases:
        enrollments = purchase.course_enrollments.all()
        progress = getattr(purchase, 'progress', None)
        
        data.append({
            'package': {
                'id': purchase.package.id,
                'title': purchase.package.title,
                'slug': purchase.package.slug,
                'thumbnail': purchase.package.thumbnail.url if purchase.package.thumbnail else None,
            },
            'purchased_at': purchase.purchased_at,
            'overall_progress': progress.overall_progress_percentage if progress else 0,
            'completed_courses': progress.completed_courses if progress else 0,
            'total_courses': purchase.package.courses.count(),
        })
    
    return Response(data)

