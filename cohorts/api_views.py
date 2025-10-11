from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Cohort, CohortSession, CohortEnrollment, CohortInstallment, CohortAttendance
from .serializers import (
    CohortSerializer, CohortDetailSerializer, CohortSessionSerializer,
    CohortEnrollmentSerializer, CohortInstallmentSerializer
)


class CohortListView(generics.ListAPIView):
    """List all active cohorts"""
    serializer_class = CohortSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Cohort.objects.filter(
            is_active=True,
            status__in=['upcoming', 'active']
        ).select_related('instructor').order_by('start_date')


class CohortDetailView(generics.RetrieveAPIView):
    """Get cohort details"""
    serializer_class = CohortDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Cohort.objects.filter(is_active=True).select_related('instructor').prefetch_related('sessions')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_cohort(request, cohort_id):
    """
    Enroll student in a cohort
    """
    cohort = get_object_or_404(Cohort, id=cohort_id, is_active=True)
    
    # Check if cohort is full
    if cohort.is_full:
        return Response(
            {'error': 'این کلاس تکمیل شده است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already enrolled
    if CohortEnrollment.objects.filter(student=request.user, cohort=cohort).exists():
        return Response(
            {'error': 'شما قبلاً در این کلاس ثبت‌نام کرده‌اید'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    payment_type = request.data.get('payment_type', 'full')
    if payment_type not in [choice[0] for choice in Cohort.PAYMENT_TYPES]:
        return Response(
            {'error': 'نوع پرداخت نامعتبر است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate total amount based on payment type
    if payment_type == 'full':
        total_amount = cohort.full_price
    elif payment_type == 'installment_3':
        total_amount = cohort.installment_3_price or cohort.full_price
    elif payment_type == 'installment_6':
        total_amount = cohort.installment_6_price or cohort.full_price
    
    with transaction.atomic():
        # Create enrollment
        enrollment = CohortEnrollment.objects.create(
            student=request.user,
            cohort=cohort,
            payment_type=payment_type,
            total_amount=total_amount,
            status='pending'
        )
        
        # Create installments if needed
        if payment_type == 'installment_3':
            installment_amount = total_amount / 3
            for i in range(1, 4):
                due_date = cohort.start_date + timedelta(days=(i-1) * 30)
                CohortInstallment.objects.create(
                    enrollment=enrollment,
                    installment_number=i,
                    amount=installment_amount,
                    due_date=due_date
                )
        elif payment_type == 'installment_6':
            installment_amount = total_amount / 6
            for i in range(1, 7):
                due_date = cohort.start_date + timedelta(days=(i-1) * 15)
                CohortInstallment.objects.create(
                    enrollment=enrollment,
                    installment_number=i,
                    amount=installment_amount,
                    due_date=due_date
                )
        
        # Update cohort enrollment count
        cohort.current_enrollments += 1
        cohort.save(update_fields=['current_enrollments'])
    
    serializer = CohortEnrollmentSerializer(enrollment)
    return Response({
        'message': 'با موفقیت در کلاس ثبت‌نام شدید',
        'enrollment': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_cohorts(request):
    """
    List user's enrolled cohorts
    """
    enrollments = CohortEnrollment.objects.filter(
        student=request.user
    ).select_related('cohort', 'cohort__instructor').order_by('-enrolled_at')
    
    data = []
    for enrollment in enrollments:
        data.append({
            'id': enrollment.id,
            'cohort': {
                'id': enrollment.cohort.id,
                'title': enrollment.cohort.title,
                'start_date': enrollment.cohort.start_date,
                'end_date': enrollment.cohort.end_date,
                'class_time': enrollment.cohort.class_time,
                'instructor': enrollment.cohort.instructor.full_name
            },
            'status': enrollment.status,
            'payment_type': enrollment.payment_type,
            'payment_status': enrollment.payment_status,
            'total_amount': float(enrollment.total_amount),
            'amount_paid': float(enrollment.amount_paid),
            'remaining_amount': float(enrollment.remaining_amount),
            'enrolled_at': enrollment.enrolled_at
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cohort_sessions(request, cohort_id):
    """
    List sessions for a cohort
    """
    cohort = get_object_or_404(Cohort, id=cohort_id)
    
    # Check if user is enrolled
    enrollment = CohortEnrollment.objects.filter(
        student=request.user, 
        cohort=cohort
    ).first()
    
    if not enrollment:
        return Response(
            {'error': 'شما در این کلاس ثبت‌نام نکرده‌اید'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    sessions = CohortSession.objects.filter(cohort=cohort).order_by('session_number')
    
    data = []
    for session in sessions:
        # Get attendance for this session
        attendance = CohortAttendance.objects.filter(
            enrollment=enrollment,
            session=session
        ).first()
        
        data.append({
            'id': session.id,
            'session_number': session.session_number,
            'title': session.title,
            'description': session.description,
            'scheduled_date': session.scheduled_date,
            'scheduled_time': session.scheduled_time,
            'duration_minutes': session.duration_minutes,
            'is_completed': session.is_completed,
            'is_recording_available': session.is_recording_available,
            'recording_url': session.recording_url,
            'attendance': {
                'is_present': attendance.is_present if attendance else False,
                'arrived_at': attendance.arrived_at if attendance else None
            }
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cohort_installments(request, enrollment_id):
    """
    List installments for an enrollment
    """
    enrollment = get_object_or_404(
        CohortEnrollment, 
        id=enrollment_id, 
        student=request.user
    )
    
    installments = CohortInstallment.objects.filter(
        enrollment=enrollment
    ).order_by('installment_number')
    
    data = []
    for installment in installments:
        data.append({
            'id': installment.id,
            'installment_number': installment.installment_number,
            'amount': float(installment.amount),
            'due_date': installment.due_date,
            'status': installment.status,
            'paid_at': installment.paid_at,
            'payment_method': installment.payment_method,
            'transaction_id': installment.transaction_id,
            'is_overdue': installment.is_overdue
        })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_attendance(request, session_id):
    """
    Mark attendance for a session (for instructors)
    """
    session = get_object_or_404(CohortSession, id=session_id)
    
    # Check if user is instructor
    if request.user != session.cohort.instructor:
        return Response(
            {'error': 'فقط مدرس کلاس می‌تواند حضور و غیاب را ثبت کند'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    student_id = request.data.get('student_id')
    is_present = request.data.get('is_present', False)
    notes = request.data.get('notes', '')
    
    if not student_id:
        return Response(
            {'error': 'شناسه دانشجو الزامی است'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    enrollment = get_object_or_404(
        CohortEnrollment, 
        id=student_id, 
        cohort=session.cohort
    )
    
    attendance, created = CohortAttendance.objects.get_or_create(
        enrollment=enrollment,
        session=session,
        defaults={
            'is_present': is_present,
            'arrived_at': timezone.now() if is_present else None,
            'notes': notes
        }
    )
    
    if not created:
        attendance.is_present = is_present
        attendance.arrived_at = timezone.now() if is_present else None
        attendance.notes = notes
        attendance.save()
    
    return Response({
        'message': 'حضور و غیاب با موفقیت ثبت شد',
        'attendance': {
            'student': enrollment.student.full_name,
            'is_present': attendance.is_present,
            'arrived_at': attendance.arrived_at
        }
    })
