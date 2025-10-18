from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import User, Notification
from app.courses.models import CoursePurchase
from app.payment.models import Order


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
    
    # Calculate financial summary
    total_spent = sum(order.total_amount for order in orders)
    
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
        'total_spent': str(total_spent),
        'pending_installments_count': pending_installments_count,
        'overdue_installments_count': overdue_installments_count,
        'total_orders': orders.count(),
    })
