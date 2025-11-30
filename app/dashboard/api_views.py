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
from datetime import timedelta
import logging
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
    """API endpoint for user login with optional OTP verification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        otp_code = request.data.get('otp_code')
        phone_number = request.data.get('phone_number')
        require_otp = request.data.get('require_otp', False)  # Optional flag to require OTP
        
        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # If OTP is required or provided, verify it
        if require_otp or otp_code:
            if not phone_number:
                # Try to get phone number from user
                phone_number = user.phone_number
                if not phone_number:
                    return Response({
                        'success': False,
                        'message': 'Phone number is required for OTP verification'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if not otp_code:
                return Response({
                    'success': False,
                    'message': 'OTP code is required',
                    'requires_otp': True
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Normalize phone number
            phone_number = phone_number.replace('+98', '').replace('0098', '').replace('-', '').replace(' ', '').strip()
            if not phone_number.startswith('0'):
                phone_number = '0' + phone_number
            
            # Verify OTP
            otp_obj = OTPCode.objects.filter(
                phone_number=phone_number,
                code=otp_code,
                purpose='login',
                is_verified=True,
                is_used=False
            ).order_by('-created_at').first()
            
            if not otp_obj:
                return Response({
                    'success': False,
                    'message': 'Invalid or unverified OTP code. Please verify your phone number first.',
                    'requires_otp': True
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_obj.is_expired():
                return Response({
                    'success': False,
                    'message': 'OTP code has expired. Please request a new one.',
                    'requires_otp': True
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            otp_obj.is_used = True
            otp_obj.save()
        
        # Login successful
        login(request, user)
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user, context={'request': request}).data
        })


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
                'message': 'All fields including phone number are required'
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
        
        # Normalize phone number
        phone_number = phone_number.replace('+98', '').replace('0098', '').replace('-', '').replace(' ', '').strip()
        if not phone_number.startswith('0'):
            phone_number = '0' + phone_number
        
        # Check if phone number is already registered
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({
                'success': False,
                'message': 'User with this phone number already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP code
        if not otp_code:
            return Response({
                'success': False,
                'message': 'OTP code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find and verify OTP
        otp_obj = OTPCode.objects.filter(
            phone_number=phone_number,
            code=otp_code,
            purpose='signup',
            is_verified=True,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            return Response({
                'success': False,
                'message': 'Invalid or unverified OTP code. Please verify your phone number first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return Response({
                'success': False,
                'message': 'OTP code has expired. Please request a new one.'
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
            
            # Generate OTP code
            otp_code = generate_otp_code(6)
            
            # Send OTP via SMS
            logger.info(f"Attempting to send OTP to {phone_number}")
            try:
                sms_result = send_otp_sms(phone_number, otp_code)
                logger.info(f"send_otp_sms returned: {sms_result}")
            except Exception as e:
                logger.error(f"Exception in send_otp_sms: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': f'Error sending OTP: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Ensure sms_result is not None
            if sms_result is None:
                logger.error("send_otp_sms returned None - this should not happen!")
                logger.error(f"Function type: {type(send_otp_sms)}")
                return Response({
                    'success': False,
                    'message': 'SMS service returned no response. Please check server logs.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Handle SMS provider rate limiting more gracefully
            if not sms_result.get('success', False):
                error_message = sms_result.get('message', 'Unknown error occurred')
                logger.error(f"SMS service returned error: {error_message}")
                
                # Normalize error message for comparison (remove extra characters, normalize whitespace)
                normalized_error = error_message.strip()
                
                # Check if it's a rate limiting error (handle variations like "کد قبلا ارسال شده!:677")
                is_rate_limit_error = (
                    'کد قبلا ارسال شده' in normalized_error or 
                    'already sent' in normalized_error.lower() or
                    'rate limit' in normalized_error.lower() or
                    'too many' in normalized_error.lower()
                )
                
                if is_rate_limit_error:
                    # Check if there's a recent valid OTP we can use
                    try:
                        valid_otp = OTPCode.objects.filter(
                            phone_number=phone_number,
                            purpose=purpose,
                            created_at__gte=timezone.now() - timedelta(minutes=5)
                        ).filter(
                            expires_at__gt=timezone.now()
                        ).exclude(
                            is_used=True
                        ).order_by('-created_at').first()
                        
                        if valid_otp:
                            logger.info(f"Rate limited but found valid OTP, returning it")
                            return Response({
                                'success': True,
                                'message': 'OTP code was already sent. Please check your phone. If you did not receive it, please wait a few minutes and try again.',
                                'expires_at': valid_otp.expires_at,
                                'already_sent': True
                            })
                    except Exception as e:
                        logger.error(f"Database error checking valid OTP: {str(e)}", exc_info=True)
                    
                    # Rate limited but no valid OTP - return 429 (not 500)
                    logger.warning(f"Rate limited for {phone_number} but no valid OTP found")
                    return Response({
                        'success': False,
                        'message': 'SMS service is temporarily unavailable due to rate limiting. Please wait 5 minutes and try again.'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    # Other SMS service errors - return 500
                    return Response({
                        'success': False,
                        'message': error_message
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Save OTP code to database
            try:
                otp_obj = OTPCode.objects.create(
                    phone_number=phone_number,
                    code=otp_code,
                    purpose=purpose,
                    expires_at=timezone.now() + timedelta(minutes=5)
                )
            except Exception as e:
                logger.error(f"Database error saving OTP: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'Failed to save OTP code. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # In development mode, return OTP code for testing
            # This helps when SMS delivery is unreliable
            from django.conf import settings
            if settings.DEBUG:
                logger.warning(f"[DEBUG MODE] OTP code for {phone_number}: {otp_code} - This should be removed in production!")
                return Response({
                    'success': True,
                    'message': 'OTP sent successfully',
                    'otp_code': otp_code,  # DEBUG ONLY - Remove in production!
                    'expires_at': otp_obj.expires_at,
                    'debug_mode': True
                })
            
            return Response({
                'success': True,
                'message': 'OTP sent successfully',
                'expires_at': otp_obj.expires_at
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
        
        otp_queryset = OTPCode.objects.filter(
            phone_number=phone_number,
            purpose=purpose,
            is_used=False
        ).order_by('-created_at')
        
        otp_obj = otp_queryset.filter(code=otp_code, is_verified=False).first()
        latest_otp = otp_queryset.filter(is_verified=False).first()
        
        sms_verified = False
        sms_error_message = None
        sms_configured = all([
            getattr(settings, 'SMS_USERNAME', ''),
            getattr(settings, 'SMS_PASSWORD', ''),
            getattr(settings, 'SMS_SENDER_NUMBER', '')
        ])
        
        # First check if OTP exists in local database
        if otp_obj:
            logger.info(f"[VerifyOTP] Found matching OTP in database for {phone_number}")
            
            # Check if expired
            if otp_obj.is_expired():
                logger.warning(f"[VerifyOTP] OTP expired for {phone_number}")
                return Response({
                    'success': False,
                    'message': 'OTP code has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # In DEBUG mode, skip SMS provider verification
            if settings.DEBUG:
                logger.info(f"[VerifyOTP] DEBUG MODE: Skipping SMS provider verification, using local database")
                otp_obj.is_verified = True
                otp_obj.verified_at = timezone.now()
                otp_obj.save()
                logger.info(f"[VerifyOTP] OTP verified successfully via DEBUG local verification for {phone_number}")
                return Response({
                    'success': True,
                    'message': 'OTP verified successfully'
                })
            
            # In production, try SMS provider verification first
            if sms_configured:
                try:
                    sms_result = verify_otp_sms(phone_number, otp_code)
                    logger.info(f"[VerifyOTP] SMS provider response: {sms_result}")
                    sms_verified = sms_result.get('success', False)
                    if sms_verified:
                        otp_obj.is_verified = True
                        otp_obj.verified_at = timezone.now()
                        otp_obj.save()
                        logger.info(f"[VerifyOTP] OTP verified successfully via SMS provider for {phone_number}")
                        return Response({
                            'success': True,
                            'message': 'OTP verified successfully'
                        })
                    else:
                        sms_error_message = sms_result.get('message')
                        logger.warning(f"[VerifyOTP] SMS provider verification failed: {sms_error_message}")
                except Exception as e:
                    sms_error_message = str(e)
                    logger.error(f"[VerifyOTP] SMS provider verification exception: {sms_error_message}", exc_info=True)
            
            # Fallback: Use local database verification if SMS fails or not configured
            # This is important for reliability when SMS provider is down
            logger.info(f"[VerifyOTP] Using local database verification fallback for {phone_number}")
            otp_obj.is_verified = True
            otp_obj.verified_at = timezone.now()
            otp_obj.save()
            logger.info(f"[VerifyOTP] OTP verified successfully via local fallback for {phone_number}")
            return Response({
                'success': True,
                'message': 'OTP verified successfully'
            })
        
        # Legacy code for SMS-only verification (kept for backwards compatibility)
        if sms_configured:
            try:
                sms_result = verify_otp_sms(phone_number, otp_code)
                logger.info(f"[VerifyOTP] SMS provider response: {sms_result}")
                sms_verified = sms_result.get('success', False)
                if not sms_verified:
                    sms_error_message = sms_result.get('message')
            except Exception as e:
                sms_error_message = str(e)
                logger.error(f"[VerifyOTP] SMS provider verification failed: {sms_error_message}", exc_info=True)
        
        if sms_verified:
            otp_to_mark = otp_obj or latest_otp
            if not otp_to_mark:
                logger.warning(f"[VerifyOTP] SMS verification succeeded but no OTP record found for {phone_number}")
                otp_to_mark = OTPCode.objects.create(
                    phone_number=phone_number,
                    code=otp_code,
                    purpose=purpose,
                    expires_at=timezone.now() + timedelta(minutes=5),
                    is_verified=True,
                    verified_at=timezone.now()
                )
                return Response({
                    'success': True,
                    'message': 'OTP verified successfully'
                })
            
            if otp_to_mark.is_expired():
                logger.warning(f"[VerifyOTP] Latest OTP expired for {phone_number}")
                return Response({
                    'success': False,
                    'message': 'OTP code has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            otp_to_mark.is_verified = True
            otp_to_mark.verified_at = timezone.now()
            otp_to_mark.save()
            
            logger.info(f"[VerifyOTP] OTP verified successfully via SMS provider for {phone_number}")
            
            return Response({
                'success': True,
                'message': 'OTP verified successfully'
            })
        
        # Fallback to local database verification when SMS verification fails/unavailable
        if not otp_obj:
            recent_otps = otp_queryset[:3]
            logger.warning(f"[VerifyOTP] No matching OTP found for {phone_number}. Provider error: {sms_error_message}. Recent OTPs: {[(o.code, o.is_verified, o.is_used, o.is_expired()) for o in recent_otps]}")
            message = sms_error_message or 'Invalid OTP code. Please check the code and try again.'
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if otp_obj.is_expired():
            logger.warning(f"[VerifyOTP] OTP expired for {phone_number}")
            return Response({
                'success': False,
                'message': 'OTP code has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        otp_obj.is_verified = True
        otp_obj.verified_at = timezone.now()
        otp_obj.save()
        
        logger.info(f"[VerifyOTP] OTP verified successfully via local fallback for {phone_number}")
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully'
        })


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
