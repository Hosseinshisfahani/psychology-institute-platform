from rest_framework import generics, status, permissions, filters, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, time
from decimal import Decimal
from .models import (
    ClinicLocation, AppointmentType, TherapistSchedule, TherapistTimeOff,
    Appointment, AppointmentCancellation, AppointmentReschedule,
    CancellationPolicy, AppointmentReminder, python_weekday_to_persian
)
from .serializers import (
    ClinicLocationSerializer, AppointmentTypeSerializer, TherapistScheduleSerializer,
    AppointmentSerializer, AppointmentListSerializer, AppointmentCreateSerializer,
    AppointmentCancellationSerializer, AppointmentRescheduleSerializer,
    CancellationPolicySerializer, AppointmentReminderSerializer,
    TherapistAvailabilitySerializer
)
from app.payment.models import Order, OrderItem, PaymentMethod, Payment
from app.payment.zarinpal import ZarinpalPayment

User = get_user_model()


class AppointmentListAPIView(generics.ListCreateAPIView):
    """List and create appointments"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'therapist', 'appointment_type', 'location']
    search_fields = [
        'therapist__first_name', 'therapist__last_name', 
        'therapist__email', 'therapist__phone_number', 'therapist__national_id',
        'client__first_name', 'client__last_name',
        'client__email', 'client__phone_number', 'client__national_id'
    ]
    ordering_fields = ['scheduled_datetime', 'created_at']
    ordering = ['-scheduled_datetime']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentListSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'therapist':
            queryset = Appointment.objects.filter(therapist=user)
        elif user.user_type == 'client':
            queryset = Appointment.objects.filter(client=user)
        else:
            # Admin or staff can see all appointments
            queryset = Appointment.objects.all()

        queryset = queryset.select_related('client', 'therapist', 'appointment_type', 'location')

        # Optional date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(scheduled_datetime__date__gte=from_date)
            except ValueError:
                pass

        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(scheduled_datetime__date__lte=to_date)
            except ValueError:
                pass

        return queryset
    
    def perform_create(self, serializer):
        # Set client to current authenticated user
        # All users (client, therapist, admin, staff) can book appointments for themselves
        serializer.save(client=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_wallet = request.data.get('use_wallet', False)
        applied_coupon = None

        with transaction.atomic():
            # Pass context to serializer to get applied coupon
            serializer.context['request'] = request
            appointment = serializer.save(client=request.user)
            
            # Increment coupon usage count if coupon was applied
            if hasattr(serializer, 'context') and 'applied_coupon' in serializer.context:
                applied_coupon = serializer.context['applied_coupon']
                if applied_coupon:
                    applied_coupon.used_count += 1
                    applied_coupon.save(update_fields=['used_count'])
            
            deposit_payload = None

            # If deposit amount is 0 after discount, mark as paid automatically
            if appointment.deposit_required and appointment.deposit_amount <= Decimal('0'):
                appointment.mark_deposit_paid()
                appointment.status = 'scheduled'
                appointment.save(update_fields=['deposit_paid', 'deposit_paid_at', 'status'])
                deposit_payload = {
                    'required': False,
                    'paid_with_wallet': False,
                    'amount': '0',
                    'free_with_coupon': True
                }
            elif appointment.deposit_required and appointment.deposit_amount > Decimal('0'):
                # Check if user wants to use wallet
                if use_wallet:
                    from app.payment.models import Wallet
                    wallet, _ = Wallet.objects.get_or_create(user=request.user)
                    
                    if wallet.balance >= appointment.deposit_amount:
                        # Use wallet to pay deposit
                        wallet.deduct_credit(
                            amount=appointment.deposit_amount,
                            transaction_type='purchase',
                            reference_id=appointment.id,
                            description=f'پرداخت ودیعه نوبت #{appointment.id}'
                        )
                        
                        # Mark deposit as paid
                        appointment.mark_deposit_paid()
                        
                        deposit_payload = {
                            'required': False,
                            'paid_with_wallet': True,
                            'amount': str(appointment.deposit_amount),
                            'wallet_balance_after': str(wallet.balance)
                        }
                    else:
                        # Partial wallet payment - use available balance
                        wallet_amount_used = wallet.balance
                        remaining_amount = appointment.deposit_amount - wallet_amount_used
                        
                        if wallet_amount_used > Decimal('0'):
                            wallet.deduct_credit(
                                amount=wallet_amount_used,
                                transaction_type='purchase',
                                reference_id=appointment.id,
                                description=f'پرداخت جزئی ودیعه نوبت #{appointment.id}'
                            )
                        
                        # Create order for remaining amount
                        deposit_payload = self._initiate_deposit_payment(
                            request.user, 
                            appointment, 
                            request=request,
                            remaining_amount=remaining_amount,
                            wallet_amount_used=wallet_amount_used
                        )
                else:
                    deposit_payload = self._initiate_deposit_payment(request.user, appointment, request=request)

        output_serializer = AppointmentSerializer(
            appointment,
            context=self.get_serializer_context()
        )
        response_data = output_serializer.data

        if deposit_payload:
            response_data['deposit'] = deposit_payload

        headers = self.get_success_headers(output_serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def _initiate_deposit_payment(self, user, appointment, request=None, remaining_amount=None, wallet_amount_used=None):
        from app.payment.api_views import get_frontend_url
        
        deposit_amount = remaining_amount if remaining_amount is not None else appointment.deposit_amount

        if deposit_amount <= Decimal('0'):
            raise serializers.ValidationError({'deposit': 'مبلغ ودیعه نامعتبر است'})

        order = Order.objects.create(
            user=user,
            subtotal=deposit_amount,
            discount_amount=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            total_amount=deposit_amount,
            payment_status='pending'
        )

        OrderItem.objects.create(
            order=order,
            item_type='appointment_deposit',
            item_id=appointment.id,
            item_title=f"ودیعه نوبت #{appointment.id}",
            quantity=1,
            unit_price=deposit_amount,
            total_price=deposit_amount
        )

        payment_method, _ = PaymentMethod.objects.get_or_create(
            payment_type='zarinpal',
            defaults={
                'name': 'زرین پال',
                'is_active': True
            }
        )

        order.payment_method = payment_method
        order.save(update_fields=['payment_method'])

        # Get frontend URL from request
        frontend_url = get_frontend_url(request=request) if request else None

        zarinpal = ZarinpalPayment()
        payment_result = zarinpal.create_payment_request(
            order,
            description=f"پرداخت ودیعه نوبت {appointment.id}",
            frontend_url=frontend_url
        )

        if not payment_result.get('success'):
            raise serializers.ValidationError({
                'deposit': payment_result.get('error', 'خطا در ایجاد پرداخت ودیعه')
            })

        payment_id = payment_result.get('payment_id')
        authority = payment_result.get('authority')
        payment_url = payment_result.get('payment_url')
        expires_at = payment_result.get('expires_at')

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:  # pragma: no cover
            raise serializers.ValidationError({'deposit': 'ثبت پرداخت ودیعه ناموفق بود'})

        appointment.deposit_order = order
        appointment.deposit_payment = payment
        appointment.save(update_fields=['deposit_order', 'deposit_payment'])

        result = {
            'required': True,
            'amount': str(deposit_amount),
            'currency': 'IRT',
            'order_id': order.id,
            'order_number': order.order_number,
            'payment_id': payment_id,
            'authority': authority,
            'payment_url': payment_url,
            'expires_at': expires_at
        }
        
        if wallet_amount_used and wallet_amount_used > Decimal('0'):
            result['wallet_used'] = str(wallet_amount_used)
            result['remaining_amount'] = str(deposit_amount)
        
        return result


class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete appointment"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'therapist':
            return Appointment.objects.filter(therapist=user)
        elif user.user_type == 'client':
            return Appointment.objects.filter(client=user)
        else:
            return Appointment.objects.all()
    
    def perform_destroy(self, instance):
        # Instead of deleting, cancel the appointment
        instance.status = 'cancelled'
        instance.save()
        
        # Create cancellation record
        AppointmentCancellation.objects.create(
            appointment=instance,
            cancelled_by=self.request.user,
            reason="لغو توسط کاربر"
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user not in [appointment.client, appointment.therapist] and not request.user.is_staff:
        return Response({'error': 'شما مجاز به تغییر این نوبت نیستید'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AppointmentRescheduleSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                reschedule = serializer.save(
                    original_appointment=appointment,
                    rescheduled_by=request.user
                )
                return Response({
                    'message': 'نوبت با موفقیت تغییر زمان شد',
                    'new_appointment_id': reschedule.new_appointment.id
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user not in [appointment.client, appointment.therapist] and not request.user.is_staff:
        return Response({'error': 'شما مجاز به لغو این نوبت نیستید'}, status=status.HTTP_403_FORBIDDEN)
    
    if appointment.status in ['cancelled', 'completed']:
        return Response({'error': 'این نوبت قبلاً لغو یا تکمیل شده است'}, status=status.HTTP_400_BAD_REQUEST)
    
    now = timezone.now()
    time_difference = appointment.scheduled_datetime - now
    within_24_hours = 0 <= time_difference.total_seconds() <= 24 * 3600
    confirm_flag = str(request.data.get('confirm', 'false')).lower() in ['true', '1', 'yes']
    is_admin_or_staff = request.user.is_staff or request.user.is_superuser
    
    # Admin/staff can bypass the 24-hour confirmation requirement
    if within_24_hours and not confirm_flag and not is_admin_or_staff:
        return Response({
            'requires_confirmation': True,
            'warning': 'در صورت کنسل کردن نوبت در این بازه زمانی، ودیعه شما بازگردانده نخواهد شد.'
        }, status=status.HTTP_200_OK)
    
    serializer = AppointmentCancellationSerializer(
        data={'reason': request.data.get('reason', '')},
        context={'appointment': appointment, 'cancelled_by': request.user}
    )
    if serializer.is_valid():
        try:
            with transaction.atomic():
                cancellation = serializer.save()

                if within_24_hours and appointment.deposit_paid:
                    cancellation.cancellation_fee = appointment.deposit_amount
                    cancellation.refund_amount = Decimal('0.00')
                    cancellation.policy_applied = 'deposit_forfeit_24h'
                    cancellation.save(update_fields=['cancellation_fee', 'refund_amount', 'policy_applied'])
                else:
                    # Calculate refund amount (outside 24h window)
                    if appointment.deposit_paid and appointment.deposit_amount > Decimal('0'):
                        # Full refund if cancelled outside 24h window
                        cancellation.refund_amount = appointment.deposit_amount
                        cancellation.cancellation_fee = Decimal('0.00')
                        cancellation.policy_applied = 'full_refund_outside_24h'
                        cancellation.save(update_fields=['refund_amount', 'cancellation_fee', 'policy_applied'])
                        
                        # Add credits to user's wallet
                        if cancellation.refund_amount > Decimal('0'):
                            from app.payment.models import Wallet
                            wallet, _ = Wallet.objects.get_or_create(user=appointment.client)
                            wallet.add_credit(
                                amount=cancellation.refund_amount,
                                transaction_type='refund',
                                reference_id=appointment.id,
                                description=f'بازگشت وجه نوبت #{appointment.id} - {appointment.appointment_type.name}'
                            )
                
                return Response({
                    'message': 'نوبت با موفقیت لغو شد',
                    'deposit_forfeit': bool(within_24_hours and appointment.deposit_paid),
                    'refund_added_to_wallet': bool(not within_24_hours and cancellation.refund_amount > Decimal('0')),
                    'refund_amount': str(cancellation.refund_amount) if cancellation.refund_amount > Decimal('0') else None,
                    'warning': 'در صورت کنسل کردن نوبت در این بازه زمانی، ودیعه شما بازگردانده نخواهد شد.' if within_24_hours else None
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TherapistListAPIView(APIView):
    """List available therapists"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        therapists = User.objects.filter(
            user_type='therapist',
            is_available=True,
            is_active=True
        ).select_related('profile')
        
        data = []
        for therapist in therapists:
            # Build absolute URL for profile image
            profile_image_url = None
            if therapist.profile_image:
                profile_image_url = request.build_absolute_uri(therapist.profile_image.url)
            
            data.append({
                'id': therapist.id,
                'name': therapist.full_name,
                'specialization': therapist.specialization,
                'experience_years': therapist.experience_years,
                'hourly_rate': float(therapist.hourly_rate),
                'profile_image': profile_image_url
            })
        return Response(data)


class TherapistDetailAPIView(APIView):
    """Get detailed information about a specific therapist"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, therapist_id):
        therapist = get_object_or_404(User, id=therapist_id, user_type='therapist')
        
        # Build absolute URL for profile image
        profile_image_url = None
        if therapist.profile_image:
            profile_image_url = request.build_absolute_uri(therapist.profile_image.url)
        
        data = {
            'id': therapist.id,
            'name': therapist.full_name,
            'specialization': therapist.specialization,
            'experience_years': therapist.experience_years,
            'hourly_rate': float(therapist.hourly_rate),
            'profile_image': profile_image_url,
            'bio': getattr(therapist, 'bio', ''),
            'license_number': therapist.license_number,
            'is_verified': getattr(therapist, 'is_verified', False),
            'is_available': therapist.is_available,
            'gender': getattr(therapist, 'gender', ''),
            'phone_number': therapist.phone_number,
            'email': therapist.email,
        }
        
        return Response(data)


class TherapistAvailabilityAPIView(APIView):
    """Get therapist's available time slots"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, therapist_id):
        therapist = get_object_or_404(User, id=therapist_id, user_type='therapist')
        date = request.query_params.get('date')
        location_id = request.query_params.get('location_id')
        
        if not date:
            return Response({'error': 'تاریخ الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'فرمت تاریخ نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get available slots
        available_slots = self._get_available_slots(therapist, target_date, location_id)
        
        return Response({
            'therapist_id': therapist.id,
            'therapist_name': therapist.full_name,
            'date': target_date,
            'available_slots': available_slots
        })
    
    def _get_available_slots(self, therapist, target_date, location_id=None):
        """Calculate available time slots for a therapist on a specific date"""
        # Convert Python weekday to Persian calendar
        day_of_week = python_weekday_to_persian(target_date.weekday())
        slots = []
        
        # Get therapist's schedule for this day
        schedules = TherapistSchedule.objects.filter(
            therapist=therapist,
            day_of_week=day_of_week,
            is_active=True
        )
        
        if location_id:
            schedules = schedules.filter(location_id=location_id)
        
        # Check if therapist is on time off
        time_off = TherapistTimeOff.objects.filter(
            therapist=therapist,
            start_date__lte=target_date,
            end_date__gte=target_date,
            is_approved=True
        ).exists()
        
        if time_off:
            return []
        
        # Generate time slots
        for schedule in schedules:
            current_time = datetime.combine(target_date, schedule.start_time)
            end_time = datetime.combine(target_date, schedule.end_time)
            
            while current_time + timedelta(minutes=60) <= end_time:
                # Check if this slot is available
                if self._is_slot_available(therapist, current_time, 60):
                    slots.append(current_time.isoformat())
                
                current_time += timedelta(minutes=15)  # 15-minute increments
        
        return slots
    
    def _is_slot_available(self, therapist, start_time, duration_minutes):
        """Check if a specific time slot is available"""
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check for overlapping appointments
        # An appointment overlaps if:
        # - It starts before the new appointment ends AND
        # - It ends after the new appointment starts
        existing_appointments = Appointment.objects.filter(
            therapist=therapist,
            status__in=['scheduled', 'confirmed', 'pending_deposit']
        )
        
        for appointment in existing_appointments:
            existing_end = appointment.scheduled_datetime + timedelta(minutes=appointment.duration_minutes)
            
            # Check if appointments overlap
            if (start_time < existing_end and end_time > appointment.scheduled_datetime):
                return False
        
        return True


class AppointmentTypeListAPIView(generics.ListAPIView):
    """List appointment types, optionally filtered by therapist specialization"""
    permission_classes = [permissions.AllowAny]
    serializer_class = AppointmentTypeSerializer
    
    def get_queryset(self):
        queryset = AppointmentType.objects.filter(is_active=True)
        
        # Filter by therapist specialization if therapist_id is provided
        therapist_id = self.request.query_params.get('therapist_id')
        if therapist_id:
            try:
                therapist = User.objects.get(id=therapist_id, user_type='therapist')
                therapist_specialization = therapist.specialization
                
                if therapist_specialization:
                    # Filter appointment types that include this specialization
                    # or have no specializations (general types)
                    # Use a more compatible approach for SQLite
                    from django.db.models import Q
                    # Filter by checking if any of the appointment type specializations
                    # match any part of the therapist's specialization
                    filtered_ids = []
                    for apt in queryset:
                        # Include general types (no specializations)
                        if not apt.specializations or len(apt.specializations) == 0:
                            filtered_ids.append(apt.id)
                        else:
                            # Check if any appointment type specialization matches
                            # any part of the therapist's specialization
                            for apt_spec in apt.specializations:
                                if apt_spec in therapist_specialization or therapist_specialization in apt_spec:
                                    filtered_ids.append(apt.id)
                                    break
                    
                    queryset = queryset.filter(id__in=filtered_ids)
            except User.DoesNotExist:
                pass
        
        return queryset


class ClinicLocationListAPIView(generics.ListAPIView):
    """List clinic locations"""
    permission_classes = [permissions.AllowAny]
    serializer_class = ClinicLocationSerializer
    queryset = ClinicLocation.objects.filter(is_active=True)


class CancellationPolicyListAPIView(generics.ListAPIView):
    """List cancellation policies"""
    permission_classes = [permissions.AllowAny]
    serializer_class = CancellationPolicySerializer
    queryset = CancellationPolicy.objects.filter(is_active=True)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def appointment_availability(request):
    """Get unavailable time slots for a specific date, therapist, and location"""
    try:
        date = request.query_params.get('date')
        therapist_id = request.query_params.get('therapist_id')
        location_id = request.query_params.get('location_id')
        
        # Safely parse duration_minutes
        try:
            duration_minutes = int(request.query_params.get('duration_minutes', 60))
        except (ValueError, TypeError):
            duration_minutes = 60
        
        if not date:
            return Response({'error': 'تاریخ الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'فرمت تاریخ نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        unavailable_times = []
        
        # If therapist_id is provided, check therapist-specific availability
        if therapist_id:
            try:
                therapist_id_int = int(therapist_id)
            except (ValueError, TypeError):
                return Response({'error': 'شناسه درمانگر نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                therapist = User.objects.get(id=therapist_id_int, user_type='therapist')
                # Convert Python weekday to Persian calendar
                day_of_week = python_weekday_to_persian(target_date.weekday())
                
                # Check if therapist has schedule for this day
                schedules = TherapistSchedule.objects.filter(
                    therapist=therapist,
                    day_of_week=day_of_week,
                    is_active=True
                )
                
                if location_id:
                    try:
                        location_id_int = int(location_id)
                        schedules = schedules.filter(location_id=location_id_int)
                    except (ValueError, TypeError):
                        # If location_id is invalid, continue without filtering by location
                        pass
                
                # If no schedule exists, all times are unavailable
                if not schedules.exists():
                    # Return all possible times as unavailable (9:00 to 21:00 in 30-min increments)
                    for hour in range(9, 22):
                        for minute in [0, 30]:
                            if hour == 21 and minute > 0:
                                break
                            unavailable_times.append(f"{hour:02d}:{minute:02d}")
                    return Response({
                        'date': str(target_date),
                        'booked_times': unavailable_times
                    })
                
                # Check if therapist is on time off
                time_off = TherapistTimeOff.objects.filter(
                    therapist=therapist,
                    start_date__lte=target_date,
                    end_date__gte=target_date,
                    is_approved=True
                ).exists()
                
                if time_off:
                    # All times are unavailable
                    for hour in range(9, 22):
                        for minute in [0, 30]:
                            if hour == 21 and minute > 0:
                                break
                            unavailable_times.append(f"{hour:02d}:{minute:02d}")
                    return Response({
                        'date': str(target_date),
                        'booked_times': unavailable_times
                    })
                
                # Get all possible time slots for the day (9:00 to 21:00 in 30-min increments)
                # Make sure to use timezone-aware datetimes for comparison with appointment datetimes
                all_slots = []
                for hour in range(9, 22):
                    for minute in [0, 30]:
                        if hour == 21 and minute > 0:
                            break
                        # Create naive datetime first
                        naive_slot_time = datetime.combine(target_date, time(hour, minute))
                        # Make it timezone-aware using the current timezone
                        slot_time = timezone.make_aware(naive_slot_time)
                        all_slots.append((slot_time, f"{hour:02d}:{minute:02d}"))
                
                # Check each slot against therapist schedule and existing appointments
                for slot_datetime, slot_time_str in all_slots:
                    slot_end = slot_datetime + timedelta(minutes=duration_minutes)
                    slot_start_time = slot_datetime.time()
                    slot_end_time = slot_end.time()
                    
                    # Check if slot is within any schedule
                    slot_in_schedule = False
                    for schedule in schedules:
                        # Check if the slot fits completely within this schedule
                        if schedule.start_time <= slot_start_time and slot_end_time <= schedule.end_time:
                            slot_in_schedule = True
                            break
                    
                    # If not in schedule, mark as unavailable
                    if not slot_in_schedule:
                        unavailable_times.append(slot_time_str)
                        continue
                    
                    # Check for overlapping appointments (across all locations for this therapist)
                    overlapping_appointments = Appointment.objects.filter(
                        therapist=therapist,
                        status__in=['scheduled', 'confirmed', 'pending_deposit']
                    )
                    
                    for appointment in overlapping_appointments:
                        existing_end = appointment.scheduled_datetime + timedelta(minutes=appointment.duration_minutes)
                        # Check if appointments overlap (both datetimes are now timezone-aware)
                        if (slot_datetime < existing_end and slot_end > appointment.scheduled_datetime):
                            unavailable_times.append(slot_time_str)
                            break
                
            except User.DoesNotExist:
                return Response({'error': 'درمانگر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error in appointment_availability: {str(e)}', exc_info=True)
                return Response({'error': f'خطا در دریافت اطلاعات: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # If no therapist_id, just return all booked times (backward compatibility)
            booked_times = Appointment.objects.filter(
                scheduled_datetime__date=target_date,
                status__in=['scheduled', 'confirmed', 'pending_deposit']
            ).values_list('scheduled_datetime', flat=True)
            
            for dt in booked_times:
                unavailable_times.append(dt.strftime('%H:%M'))
        
        return Response({
            'date': str(target_date),
            'booked_times': unavailable_times
        })
    except Exception as e:
        # Catch any unexpected errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Unexpected error in appointment_availability: {str(e)}', exc_info=True)
        return Response({'error': 'خطای سرور در دریافت اطلاعات'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_statistics(request):
    """Get appointment statistics for dashboard"""
    user = request.user
    
    if user.user_type == 'therapist':
        appointments = Appointment.objects.filter(therapist=user)
    elif user.user_type == 'client':
        appointments = Appointment.objects.filter(client=user)
    else:
        appointments = Appointment.objects.all()
    
    stats = {
        'total_appointments': appointments.count(),
        'scheduled': appointments.filter(status='scheduled').count(),
        'confirmed': appointments.filter(status='confirmed').count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
        'upcoming': appointments.filter(
            status__in=['scheduled', 'confirmed'],
            scheduled_datetime__gte=timezone.now()
        ).count()
    }
    
    return Response(stats)
