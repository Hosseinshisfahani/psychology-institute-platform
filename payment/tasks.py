"""
Celery tasks for payment processing and reminders
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='payment.send_installment_reminders')
def send_installment_reminders():
    """
    Send reminders for upcoming and overdue installment payments
    Runs daily to check for payments due within 3 days
    """
    from workshops.models import InstallmentPayment
    
    today = timezone.now().date()
    reminder_date = today + timedelta(days=3)
    
    # Get payments that are due within 3 days and haven't been reminded yet
    upcoming_payments = InstallmentPayment.objects.filter(
        status='pending',
        due_date__lte=reminder_date,
        due_date__gte=today,
        reminder_sent=False
    ).select_related('plan__registration__user', 'plan__registration__workshop')
    
    reminder_count = 0
    
    for payment in upcoming_payments:
        try:
            user = payment.plan.registration.user
            workshop = payment.plan.registration.workshop
            
            # Calculate days until due
            days_until_due = (payment.due_date - today).days
            
            # Prepare email context
            context = {
                'user': user,
                'workshop': workshop,
                'payment': payment,
                'days_until_due': days_until_due,
                'plan': payment.plan,
            }
            
            # Send email notification
            subject = f'یادآوری پرداخت قسط کارگاه {workshop.title}'
            message = render_to_string('payment/emails/installment_reminder.html', context)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            # Mark reminder as sent
            payment.reminder_sent = True
            payment.reminder_sent_at = timezone.now()
            payment.save(update_fields=['reminder_sent', 'reminder_sent_at'])
            
            reminder_count += 1
            logger.info(f"Sent installment reminder to {user.email} for payment #{payment.installment_number}")
            
        except Exception as e:
            logger.error(f"Error sending installment reminder for payment {payment.id}: {str(e)}")
            continue
    
    logger.info(f"Sent {reminder_count} installment payment reminders")
    return reminder_count


@shared_task(name='payment.update_overdue_installments')
def update_overdue_installments():
    """
    Mark installment payments as overdue when they pass their due date
    Runs daily
    """
    from workshops.models import InstallmentPayment
    
    today = timezone.now().date()
    
    # Get pending payments that are past due date
    overdue_payments = InstallmentPayment.objects.filter(
        status='pending',
        due_date__lt=today
    )
    
    updated_count = overdue_payments.update(status='overdue')
    
    # Send overdue notifications
    for payment in overdue_payments:
        try:
            user = payment.plan.registration.user
            workshop = payment.plan.registration.workshop
            
            # Calculate days overdue
            days_overdue = (today - payment.due_date).days
            
            context = {
                'user': user,
                'workshop': workshop,
                'payment': payment,
                'days_overdue': days_overdue,
                'plan': payment.plan,
            }
            
            # Send overdue notification
            subject = f'قسط معوق کارگاه {workshop.title}'
            message = render_to_string('payment/emails/installment_overdue.html', context)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Sent overdue notification to {user.email} for payment #{payment.installment_number}")
            
        except Exception as e:
            logger.error(f"Error sending overdue notification for payment {payment.id}: {str(e)}")
            continue
    
    logger.info(f"Marked {updated_count} payments as overdue")
    return updated_count


@shared_task(name='payment.check_installment_completion')
def check_installment_completion():
    """
    Check if installment plans are fully paid and update registration status
    Runs daily
    """
    from workshops.models import InstallmentPlan, WorkshopRegistration
    
    # Get all installment plans
    plans = InstallmentPlan.objects.filter(
        registration__status='pending_payment'
    ).select_related('registration')
    
    activated_count = 0
    
    for plan in plans:
        if plan.is_fully_paid:
            registration = plan.registration
            registration.status = 'active'
            registration.save(update_fields=['status'])
            activated_count += 1
            
            logger.info(f"Activated registration {registration.id} after full payment")
    
    logger.info(f"Activated {activated_count} workshop registrations")
    return activated_count


@shared_task(name='payment.process_workshop_payment')
def process_workshop_payment(payment_id, registration_id):
    """
    Process workshop payment and update registration status
    Called after successful payment
    """
    from workshops.models import WorkshopRegistration, InstallmentPayment
    from payment.models import Payment
    
    try:
        payment = Payment.objects.get(id=payment_id)
        registration = WorkshopRegistration.objects.get(id=registration_id)
        
        if payment.status == 'completed':
            if registration.payment_type == 'full_payment':
                # Full payment - activate immediately
                registration.status = 'active'
                registration.amount_paid = payment.amount
                registration.save(update_fields=['status', 'amount_paid'])
                
                logger.info(f"Activated workshop registration {registration.id} after full payment")
                
            elif registration.payment_type == 'installment':
                # Installment payment - update installment record
                installment = InstallmentPayment.objects.filter(
                    plan__registration=registration,
                    order=payment.order
                ).first()
                
                if installment:
                    installment.status = 'paid'
                    installment.paid_at = timezone.now()
                    installment.transaction_id = payment.gateway_transaction_id
                    installment.save(update_fields=['status', 'paid_at', 'transaction_id'])
                    
                    # Update registration amount paid
                    registration.amount_paid += installment.amount
                    
                    # Check if first installment - activate registration
                    if installment.installment_number == 1:
                        registration.status = 'active'
                    
                    registration.save(update_fields=['amount_paid', 'status'])
                    
                    logger.info(f"Processed installment {installment.installment_number} for registration {registration.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing workshop payment: {str(e)}")
        return False


@shared_task(name='payment.send_payment_receipt')
def send_payment_receipt(payment_id):
    """
    Send payment receipt email to user
    """
    from payment.models import Payment
    
    try:
        payment = Payment.objects.select_related('order__user').get(id=payment_id)
        user = payment.order.user
        
        context = {
            'user': user,
            'payment': payment,
            'order': payment.order,
        }
        
        subject = f'رسید پرداخت - سفارش {payment.order.order_number}'
        message = render_to_string('payment/emails/payment_receipt.html', context)
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent payment receipt to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending payment receipt: {str(e)}")
        return False

