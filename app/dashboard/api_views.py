from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .models import User, Notification
from .serializers import UserSerializer, UserProfileSerializer
from app.courses.models import CoursePurchase
from app.payment.models import Order


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stats_api(request):
    """
    API endpoint for dashboard statistics
    """
    user = request.user
    
    # Get basic user stats
    stats = {
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'date_joined': user.date_joined,
        },
        'notifications': {
            'unread_count': Notification.objects.filter(user=user, is_read=False).count(),
            'total_count': Notification.objects.filter(user=user).count(),
        }
    }
    
    # Try to get additional stats from other apps
    try:
        from app.courses.models import CoursePurchase
        from app.payment.models import Order
        
        # Course stats
        course_purchases = CoursePurchase.objects.filter(user=user)
        stats['courses'] = {
            'total_purchased': course_purchases.count(),
            'total_spent': sum(purchase.amount_paid for purchase in course_purchases),
        }
        
        # Order stats
        orders = Order.objects.filter(user=user)
        stats['orders'] = {
            'total_orders': orders.count(),
            'total_spent': sum(order.total_amount for order in orders),
        }
        
    except ImportError:
        # Apps not available
        stats['courses'] = {'total_purchased': 0, 'total_spent': 0}
        stats['orders'] = {'total_orders': 0, 'total_spent': 0}
    
    # Try to get workshop stats
    try:
        from app.workshops.models import WorkshopRegistration
        workshop_registrations = WorkshopRegistration.objects.filter(user=user)
        stats['workshops'] = {
            'total_registered': workshop_registrations.count(),
            'total_spent': sum(registration.amount_paid for registration in workshop_registrations),
        }
    except ImportError:
        stats['workshops'] = {'total_registered': 0, 'total_spent': 0}
    
    # Try to get package stats
    try:
        from app.packages.models import PackagePurchase
        package_purchases = PackagePurchase.objects.filter(user=user)
        stats['packages'] = {
            'total_purchased': package_purchases.count(),
            'total_spent': sum(purchase.amount_paid for purchase in package_purchases),
        }
    except ImportError:
        stats['packages'] = {'total_purchased': 0, 'total_spent': 0}
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def financial_report_api(request):
    """
    API endpoint for financial report data
    """
    user = request.user
    
    # Import models here to avoid circular imports
    try:
        from app.workshops.models import WorkshopRegistration, InstallmentPayment
        from app.packages.models import PackagePurchase
        
        # Get all workshop registrations with installment plans
        workshop_registrations = WorkshopRegistration.objects.filter(
            user=user
        ).select_related('workshop', 'installment_plan').prefetch_related(
            'installment_plan__payments'
        )
        
        # Serialize workshop registrations
        workshops_data = []
        for registration in workshop_registrations:
            workshop_data = {
                'id': registration.id,
                'workshop': {
                    'id': registration.workshop.id,
                    'title': registration.workshop.title,
                    'slug': registration.workshop.slug,
                },
                'status': registration.status,
                'payment_type': registration.payment_type,
                'amount_paid': str(registration.amount_paid),
                'total_amount': str(registration.total_amount),
                'progress_percentage': registration.progress_percentage,
                'registered_at': registration.registered_at,
            }
            
            if hasattr(registration, 'installment_plan'):
                plan = registration.installment_plan
                payments_data = []
                for payment in plan.payments.all().order_by('installment_number'):
                    payments_data.append({
                        'id': payment.id,
                        'installment_number': payment.installment_number,
                        'amount': str(payment.amount),
                        'due_date': payment.due_date,
                        'due_date_persian': payment.due_date.strftime('%Y/%m/%d') if payment.due_date else None,
                        'status': payment.status,
                        'paid_at': payment.paid_at,
                        'is_overdue': payment.is_overdue,
                    })
                
                workshop_data['installment_plan'] = {
                    'total_amount': str(plan.total_amount),
                    'number_of_installments': plan.number_of_installments,
                    'installment_amount': str(plan.installment_amount),
                    'total_paid': str(plan.total_paid),
                    'remaining_amount': str(plan.remaining_amount),
                    'is_fully_paid': plan.is_fully_paid,
                    'payments': payments_data,
                }
            
            workshops_data.append(workshop_data)
        
        # Get all package purchases
        package_purchases = PackagePurchase.objects.filter(
            user=user
        ).select_related('package').order_by('-purchased_at')
        
        packages_data = []
        for purchase in package_purchases:
            package_data = {
                'id': purchase.id,
                'package': {
                    'id': purchase.package.id,
                    'title': purchase.package.title,
                    'slug': purchase.package.slug,
                },
                'amount_paid': str(purchase.amount_paid),
                'purchased_at': purchase.purchased_at,
            }
            
            if hasattr(purchase, 'progress'):
                progress = purchase.progress
                package_data['progress'] = {
                    'overall_progress_percentage': progress.overall_progress_percentage,
                    'completed_courses': progress.completed_courses,
                    'total_courses': purchase.package.courses.count(),
                }
            
            packages_data.append(package_data)
        
        # Get installment payments
        installment_payments = []
        for registration in workshop_registrations:
            if hasattr(registration, 'installment_plan'):
                plan = registration.installment_plan
                payments = plan.payments.all().order_by('installment_number')
                for payment in payments:
                    installment_payments.append({
                        'id': payment.id,
                        'installment_number': payment.installment_number,
                        'amount': str(payment.amount),
                        'due_date': payment.due_date,
                        'due_date_persian': payment.due_date.strftime('%Y/%m/%d') if payment.due_date else None,
                        'status': payment.status,
                        'paid_at': payment.paid_at,
                        'is_overdue': payment.is_overdue,
                    })
        
    except ImportError:
        # Workshops and packages apps not yet installed
        workshops_data = []
        packages_data = []
        installment_payments = []
    
    # Get course purchases
    course_purchases = CoursePurchase.objects.filter(
        user=user
    ).select_related('course').order_by('-purchased_at')
    
    courses_data = []
    for purchase in course_purchases:
        courses_data.append({
            'id': purchase.id,
            'course': {
                'id': purchase.course.id,
                'title': purchase.course.title,
                'slug': purchase.course.slug,
            },
            'amount_paid': str(purchase.amount_paid),
            'purchased_at': purchase.purchased_at,
        })
    
    # Get orders
    orders = Order.objects.filter(user=user).order_by('-created_at')
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'total_amount': str(order.total_amount),
            'created_at': order.created_at,
        })
    
    # Get successful payments (completed payments)
    from app.payment.models import Payment
    successful_payments = Payment.objects.filter(
        order__user=user,
        status='completed'
    ).select_related('order', 'payment_method').order_by('-completed_at', '-created_at')
    
    payments_data = []
    for payment in successful_payments:
        # Get workshop info if this payment is for a workshop
        workshop_title = None
        for item in payment.order.items.all():
            if item.item_type == 'workshop':
                try:
                    from app.workshops.models import Workshop
                    workshop = Workshop.objects.get(id=item.item_id)
                    workshop_title = workshop.title
                    break
                except:
                    pass
        
        payments_data.append({
            'id': payment.id,
            'order_number': payment.order.order_number,
            'order_id': payment.order.id,
            'amount': str(payment.amount),
            'payment_method': payment.payment_method.name if payment.payment_method else 'نامشخص',
            'transaction_id': payment.gateway_transaction_id or payment.gateway_response.get('ref_id', ''),
            'workshop_title': workshop_title,
            'completed_at': payment.completed_at or payment.created_at,
            'created_at': payment.created_at,
        })
    
    # Get remaining installments (pending installments with details)
    remaining_installments = []
    for registration in workshop_registrations:
        if hasattr(registration, 'installment_plan'):
            plan = registration.installment_plan
            pending_payments = plan.payments.filter(status='pending').order_by('installment_number')
            for payment in pending_payments:
                remaining_installments.append({
                    'id': payment.id,
                    'workshop_title': registration.workshop.title,
                    'workshop_slug': registration.workshop.slug,
                    'installment_number': payment.installment_number,
                    'total_installments': plan.number_of_installments,
                    'amount': str(payment.amount),
                    'due_date': payment.due_date,
                    'due_date_persian': payment.due_date.strftime('%Y/%m/%d') if payment.due_date else None,
                    'is_overdue': payment.is_overdue,
                    'registration_id': registration.id,
                })
    
    # Calculate financial summary
    total_spent = sum(order.total_amount for order in orders if order.payment_status == 'completed')
    
    # Count pending installments
    pending_installments_count = sum(
        1 for payment in installment_payments
        if payment['status'] == 'pending'
    )
    
    overdue_installments_count = sum(
        1 for payment in installment_payments
        if payment['status'] == 'overdue'
    )
    
    return Response({
        'orders': orders_data,
        'workshop_registrations': workshops_data,
        'package_purchases': packages_data,
        'course_purchases': courses_data,
        'installment_payments': installment_payments,
        'successful_payments': payments_data,
        'remaining_installments': remaining_installments,
        'total_spent': str(total_spent),
        'pending_installments_count': pending_installments_count,
        'overdue_installments_count': overdue_installments_count,
        'total_orders': orders.count(),
    })


class LoginAPIView(APIView):
    """API endpoint for user login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': UserSerializer(user, context={'request': request}).data
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)


class SignupAPIView(APIView):
    """API endpoint for user signup"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        
        # Validate required fields
        if not all([email, password1, password2, first_name, last_name]):
            return Response({
                'success': False,
                'message': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if passwords match
        if password1 != password2:
            return Response({
                'success': False,
                'message': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return Response({
                'success': True,
                'message': 'Signup successful',
                'user': UserSerializer(user, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """API endpoint for user logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({
            'success': True,
            'message': 'Logout successful'
        })


class AuthCheckAPIView(APIView):
    """API endpoint to check authentication status"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user, context={'request': request})
            return Response({
                'authenticated': True,
                'user': serializer.data
            })
        else:
            return Response({
                'authenticated': False,
                'user': None
            })


class ProfileAPIView(APIView):
    """API endpoint for user profile"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
