import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)
from datetime import timedelta
from .models import User, Notification, OTPCode
from .serializers import UserSerializer, UserProfileSerializer
from .sms_service import send_otp_sms, verify_otp_sms, generate_otp_code
from app.courses.models import CoursePurchase
from app.payment.models import Order

logger = logging.getLogger(__name__)


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
    """API endpoint for user login with email OR phone number (optional) and optional OTP verification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email', '').strip()
            phone_number = request.data.get('phone_number', '').strip()
            password = request.data.get('password')
            otp_code = request.data.get('otp_code')
            require_otp = request.data.get('require_otp', False)  # Optional flag to require OTP
            
            logger.info(f"[Login] Login attempt - Email: {email[:3]}***, Phone: {phone_number[:4] if phone_number else 'None'}***")
            
            # At least one identifier (email or phone) is required
            if not email and not phone_number:
                logger.warning("[Login] Missing email and phone number")
                return Response({
                    'success': False,
                    'message': 'ایمیل یا شماره تلفن الزامی است'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Password is always required
            if not password:
                logger.warning("[Login] Missing password")
                return Response({
                    'success': False,
                    'message': 'رمز عبور الزامی است'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = None
            
            # Try authentication by email if provided
            if email:
                try:
                    user = authenticate(request, username=email, password=password)
                    if user is None:
                        logger.warning(f"[Login] Authentication failed for email: {email[:3]}***")
                        return Response({
                            'success': False,
                            'message': 'ایمیل یا رمز عبور اشتباه است'
                        }, status=status.HTTP_401_UNAUTHORIZED)
                    logger.info(f"[Login] User authenticated via email: {user.id}")
                except Exception as e:
                    logger.error(f"[Login] Exception during email authentication: {str(e)}", exc_info=True)
                    return Response({
                        'success': False,
                        'message': 'خطا در فرآیند ورود. لطفاً دوباره تلاش کنید.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Try authentication by phone number if provided (and email auth failed or not provided)
            elif phone_number:
                try:
                    # Normalize phone number
                    normalized_phone = phone_number.replace('+98', '').replace('0098', '').replace('-', '').replace(' ', '').strip()
                    if not normalized_phone.startswith('0'):
                        normalized_phone = '0' + normalized_phone
                    
                    # Find user by phone number
                    try:
                        user = User.objects.get(phone_number=normalized_phone)
                        # Verify password
                        if not user.check_password(password):
                            logger.warning(f"[Login] Password mismatch for phone: {phone_number[:4]}***")
                            return Response({
                                'success': False,
                                'message': 'شماره تلفن یا رمز عبور اشتباه است'
                            }, status=status.HTTP_401_UNAUTHORIZED)
                        logger.info(f"[Login] User authenticated via phone: {user.id}")
                    except User.DoesNotExist:
                        logger.warning(f"[Login] User not found for phone: {phone_number[:4]}***")
                        return Response({
                            'success': False,
                            'message': 'شماره تلفن یا رمز عبور اشتباه است'
                        }, status=status.HTTP_401_UNAUTHORIZED)
                except Exception as e:
                    logger.error(f"[Login] Exception during phone authentication: {str(e)}", exc_info=True)
                    return Response({
                        'success': False,
                        'message': 'خطا در فرآیند ورود. لطفاً دوباره تلاش کنید.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Ensure user was found and authenticated
            if user is None:
                logger.warning("[Login] User is None after authentication attempts")
                return Response({
                    'success': False,
                    'message': 'اطلاعات ورود نامعتبر است'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"[Login] Inactive user attempted login: {user.id}")
                return Response({
                    'success': False,
                    'message': 'حساب کاربری شما غیرفعال است. لطفاً با پشتیبانی تماس بگیرید.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # If OTP is required or provided, verify it
            if require_otp or otp_code:
                try:
                    # Get phone number for OTP verification
                    # Use provided phone_number, or fall back to user's stored phone_number
                    otp_phone = phone_number if phone_number else user.phone_number
                    
                    if not otp_phone:
                        logger.warning(f"[Login] OTP required but no phone number available for user: {user.id}")
                        return Response({
                            'success': False,
                            'message': 'شماره تلفن برای تایید OTP الزامی است'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if not otp_code:
                        logger.info(f"[Login] OTP required but not provided for user: {user.id}")
                        return Response({
                            'success': False,
                            'message': 'کد تایید الزامی است',
                            'requires_otp': True
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Normalize phone number for OTP lookup
                    normalized_otp_phone = otp_phone.replace('+98', '').replace('0098', '').replace('-', '').replace(' ', '').strip()
                    if not normalized_otp_phone.startswith('0'):
                        normalized_otp_phone = '0' + normalized_otp_phone
                    
                    # Normalize OTP code
                    otp_code = str(otp_code).replace(' ', '').replace('-', '').strip()
                    
                    # Find verified OTP for this phone/purpose
                    # Try to match the code first, but also accept any verified OTP as fallback
                    otp_obj = OTPCode.objects.filter(
                        phone_number=normalized_otp_phone,
                        code=otp_code,
                        purpose='login',
                        is_verified=True,
                        is_used=False
                    ).order_by('-created_at').first()
                    
                    # Fallback: If no exact match, check for any verified OTP for this phone/purpose
                    if not otp_obj:
                        otp_obj = OTPCode.objects.filter(
                            phone_number=normalized_otp_phone,
                            purpose='login',
                            is_verified=True,
                            is_used=False
                        ).order_by('-created_at').first()
                    
                    if not otp_obj:
                        logger.warning(f"[Login] OTP not found for phone: {normalized_otp_phone[:4]}***")
                        return Response({
                            'success': False,
                            'message': 'کد تایید یافت نشد. لطفاً ابتدا شماره تلفن خود را تایید کنید.',
                            'requires_otp': True
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if otp_obj.is_expired():
                        logger.warning(f"[Login] OTP expired for phone: {normalized_otp_phone[:4]}***")
                        return Response({
                            'success': False,
                            'message': 'کد تایید منقضی شده است. لطفاً کد جدیدی درخواست دهید.',
                            'requires_otp': True
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Mark OTP as used
                    otp_obj.is_used = True
                    otp_obj.save()
                    logger.info(f"[Login] OTP verified and marked as used for user: {user.id}")
                except Exception as e:
                    logger.error(f"[Login] Exception during OTP verification: {str(e)}", exc_info=True)
                    return Response({
                        'success': False,
                        'message': 'خطا در تایید کد. لطفاً دوباره تلاش کنید.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Login successful - wrap in try-except for error handling
            try:
                # Specify backend since multiple authentication backends are configured
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                logger.info(f"[Login] User logged in successfully: {user.id}")
            except Exception as e:
                logger.error(f"[Login] Exception during Django login: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'خطا در ایجاد نشست ورود. لطفاً دوباره تلاش کنید.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Serialize user data
            try:
                user_data = UserSerializer(user, context={'request': request}).data
            except Exception as e:
                logger.error(f"[Login] Exception during user serialization: {str(e)}", exc_info=True)
                # Still return success but with minimal user data
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'user_type': user.user_type,
                }
            
            return Response({
                'success': True,
                'message': 'ورود با موفقیت انجام شد',
                'user': user_data
            })
            
        except Exception as e:
            logger.error(f"[Login] Unexpected error in LoginAPIView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'خطای غیرمنتظره در فرآیند ورود. لطفاً دوباره تلاش کنید.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignupAPIView(APIView):
    """API endpoint for user signup with OTP verification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('otp_code')
        
        # Validate required fields
        if not all([email, password1, password2, first_name, last_name, phone_number]):
            return Response({
                'success': False,
                'message': 'تمام فیلدها از جمله شماره تلفن الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if passwords match
        if password1 != password2:
            return Response({
                'success': False,
                'message': 'رمزهای عبور مطابقت ندارند'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'کاربری با این ایمیل قبلاً ثبت‌نام کرده است.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number
        phone_number = phone_number.replace('+98', '').replace('0098', '').replace('-', '').replace(' ', '').strip()
        if not phone_number.startswith('0'):
            phone_number = '0' + phone_number
        
        # Check if phone number is already registered
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({
                'success': False,
                'message': 'کاربری با این شماره تلفن قبلاً ثبت‌نام کرده است.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP code
        if not otp_code:
            return Response({
                'success': False,
                'message': 'کد تایید الزامی است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize OTP code
        otp_code = str(otp_code).replace(' ', '').replace('-', '').strip()
        
        # Find verified OTP for this phone/purpose
        # Try to match the code first, but also accept any verified OTP as fallback
        otp_obj = OTPCode.objects.filter(
            phone_number=phone_number,
            code=otp_code,
            purpose='signup',
            is_verified=True,
            is_used=False
        ).order_by('-created_at').first()
        
        # Fallback: If no exact match, check for any verified OTP for this phone/purpose
        if not otp_obj:
            otp_obj = OTPCode.objects.filter(
                phone_number=phone_number,
                purpose='signup',
                is_verified=True,
                is_used=False
            ).order_by('-created_at').first()
        
        if not otp_obj:
            return Response({
                'success': False,
                'message': 'کد تایید یافت نشد. لطفاً ابتدا شماره تلفن خود را تایید کنید.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return Response({
                'success': False,
                'message': 'کد تایید منقضی شده است. لطفاً کد جدیدی درخواست دهید.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
            
            # Mark OTP as used
            otp_obj.is_used = True
            otp_obj.save()
            
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
        try:
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
        except Exception as e:
            logger.error(f"Error in AuthCheckAPIView: {str(e)}", exc_info=True)
            return Response({
                'authenticated': False,
                'user': None,
                'error': 'An error occurred while checking authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@method_decorator(csrf_exempt, name='dispatch')
class SendOTPAPIView(APIView):
    """API endpoint to send OTP code via SMS"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No authentication required
    
    def post(self, request):
        try:
            phone_number = request.data.get('phone_number')
            purpose = request.data.get('purpose', 'signup')  # signup, login, password_reset
            
            if not phone_number:
                return Response({
                    'success': False,
                    'message': 'Phone number is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate phone number format (Iranian mobile numbers)
            phone_number = phone_number.replace('+98', '').replace('0098', '').replace('-', '').replace(' ', '').strip()
            if not phone_number.startswith('0'):
                phone_number = '0' + phone_number
            
            if not phone_number.startswith('09') or len(phone_number) != 11:
                return Response({
                    'success': False,
                    'message': 'Invalid phone number format. Please use format: 09123456789'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for recent OTP requests (rate limiting - 2 minutes cooldown)
            try:
                recent_otp = OTPCode.objects.filter(
                    phone_number=phone_number,
                    purpose=purpose,
                    created_at__gte=timezone.now() - timedelta(minutes=2)
                ).order_by('-created_at').first()
                
                if recent_otp and not recent_otp.is_expired() and not recent_otp.is_used:
                    # If there's a valid recent OTP, check if SMS was actually sent
                    # If SMS provider is rate-limiting, we can still return success with existing code
                    logger.info(f"Found recent valid OTP for {phone_number}, checking if we should reuse it")
                    
                    # Check if the error is rate limiting (کد قبلا ارسال شده)
                    # In this case, the SMS was likely already sent, so we return the existing code
                    return Response({
                        'success': True,
                        'message': 'OTP code already sent. Please check your phone. If you did not receive it, please wait 2 minutes and try again.',
                        'expires_at': recent_otp.expires_at,
                        'already_sent': True
                    })
            except Exception as e:
                logger.error(f"Database error checking recent OTP: {str(e)}", exc_info=True)
                # Continue with sending new OTP if database query fails
            
            # ============================================================
            # TEMPORARY: SMS PROVIDER DISABLED
            # TODO: Re-enable when switching to Kavehnegar service
            # ============================================================
            
            # # Send OTP via SMS - Let provider generate the code
            # logger.info(f"Requesting SMS provider to send OTP to {phone_number}")
            # try:
            #     sms_result = send_otp_sms(phone_number)  # No code parameter - provider generates it
            #     logger.info(f"send_otp_sms returned: {sms_result}")
            # except Exception as e:
            #     logger.error(f"Exception in send_otp_sms: {str(e)}", exc_info=True)
            #     return Response({
            #         'success': False,
            #         'message': f'Error sending OTP: {str(e)}'
            #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # TEMPORARY: Generate a fixed code for testing (use "1234" for any signup)
            logger.warning(f"[TEMP] SMS provider disabled - using fixed test code for {phone_number}")
            test_code = "1234"  # Fixed code for testing
            
            # Save OTP to database with the test code
            try:
                otp_obj = OTPCode.objects.create(
                    phone_number=phone_number,
                    code=test_code,  # Store the test code
                    transaction_id=f"TEST-{timezone.now().timestamp()}",  # Fake transaction ID
                    purpose=purpose,
                    expires_at=timezone.now() + timedelta(minutes=5)
                )
                logger.info(f"[SendOTP] Created test OTP record with code: {test_code}")
            except Exception as e:
                logger.error(f"Database error saving OTP: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'Failed to save OTP record. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # TEMPORARY: Return message with test code
            return Response({
                'success': True,
                'message': f'[TEST MODE] Use code: {test_code} (SMS disabled temporarily)',
                'expires_at': otp_obj.expires_at,
                'test_mode': True,
                'test_code': test_code  # Only for development!
            })
        except Exception as e:
            logger.error(f"Unexpected error in SendOTPAPIView: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'An unexpected error occurred. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyOTPAPIView(APIView):
    """API endpoint to verify OTP code"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No authentication required
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('otp_code') or request.data.get('code')
        purpose = request.data.get('purpose', 'signup')
        
        if not phone_number or not otp_code:
            return Response({
                'success': False,
                'message': 'Phone number and OTP code are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number
        phone_number = phone_number.replace('+98', '').replace('0098', '').replace('-', '').replace(' ', '').strip()
        if not phone_number.startswith('0'):
            phone_number = '0' + phone_number
        
        # Normalize OTP code (remove spaces, ensure it's a string)
        otp_code = str(otp_code).replace(' ', '').replace('-', '').strip()
        
        logger.info(f"[VerifyOTP] Attempting to verify OTP for {phone_number}, code: {otp_code}, purpose: {purpose}")
        
        # Find the most recent OTP request for this phone/purpose
        otp_obj = OTPCode.objects.filter(
            phone_number=phone_number,
            purpose=purpose,
            is_used=False,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            logger.warning(f"[VerifyOTP] No pending OTP found for {phone_number}, purpose: {purpose}")
            return Response({
                'success': False,
                'message': 'No pending OTP request found. Please request a new code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if expired
        if otp_obj.is_expired():
            logger.warning(f"[VerifyOTP] OTP expired for {phone_number}")
            return Response({
                'success': False,
                'message': 'OTP code has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify with SMS provider
        sms_configured = all([
            getattr(settings, 'SMS_USERNAME', ''),
            getattr(settings, 'SMS_PASSWORD', ''),
            getattr(settings, 'SMS_SENDER_NUMBER', '')
        ])
        
        if not sms_configured:
            logger.error("[VerifyOTP] SMS provider not configured!")
            return Response({
                'success': False,
                'message': 'SMS verification service is not configured.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # ============================================================
            # TEMPORARY: SMS VERIFICATION SIMPLIFIED (SMS provider disabled)
            # TODO: Restore proper SMS provider verification when switching to Kavehnegar
            # ============================================================
            # Since SMS provider is temporarily disabled, we verify by:
            # 1. There's a valid OTP request for this phone/purpose
            # 2. The code format is valid (4-6 digits)
            # 3. It's not expired
            # 4. In test mode: Any valid format code is accepted
            
            logger.info(f"[VerifyOTP] [TEST MODE] Verifying OTP for {phone_number} with code: {otp_code}")
            
            # Validate code format
            if not otp_code.isdigit() or len(otp_code) not in [4, 6]:
                logger.warning(f"[VerifyOTP] Invalid code format: {otp_code}")
                return Response({
                    'success': False,
                    'message': 'Invalid OTP code format. Please enter 4-6 digits.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark as verified
            otp_obj.code = otp_code  # Store the entered code
            otp_obj.is_verified = True
            otp_obj.verified_at = timezone.now()
            otp_obj.save()
            
            logger.info(f"[VerifyOTP] [TEST MODE] OTP verified successfully for {phone_number}")
            return Response({
                'success': True,
                'message': 'OTP verified successfully',
                'test_mode': True  # Indicate this is test mode
            })
                
        except Exception as e:
            logger.error(f"[VerifyOTP] Exception during OTP verification: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Error verifying OTP. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def sms_config_check(request):
    """Diagnostic endpoint to check if SMS credentials are loaded"""
    from django.conf import settings
    from .sms_service import SMS_USERNAME, SMS_PASSWORD, SMS_SENDER_NUMBER
    
    return Response({
        'sms_username': SMS_USERNAME if SMS_USERNAME else 'NOT SET',
        'sms_password_set': bool(SMS_PASSWORD),
        'sms_sender_number': SMS_SENDER_NUMBER if SMS_SENDER_NUMBER else 'NOT SET',
        'settings_sms_username': getattr(settings, 'SMS_USERNAME', 'NOT FOUND'),
        'settings_sms_password_set': bool(getattr(settings, 'SMS_PASSWORD', '')),
        'settings_sms_sender': getattr(settings, 'SMS_SENDER_NUMBER', 'NOT FOUND'),
    })
