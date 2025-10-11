from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from payment.models import Order, OrderItem
from .models import Course, Enrollment, CoursePurchase


@receiver(post_save, sender=Order)
def handle_course_purchase(sender, instance, created, **kwargs):
    """
    Handle course purchases when order is paid
    """
    if instance.status == 'paid' and instance.payment_status == 'completed':
        # Get all course items in the order
        course_items = instance.items.filter(item_type='course')
        
        for item in course_items:
            try:
                course = Course.objects.get(id=item.item_id)
                
                # Create course purchase record
                purchase, created = CoursePurchase.objects.get_or_create(
                    user=instance.user,
                    course=course,
                    defaults={
                        'amount_paid': item.total_price,
                        'original_price': course.price,
                        'discount_amount': course.price - item.unit_price,
                        'purchased_at': timezone.now(),
                        'payment_method': 'Zarinpal',
                        'transaction_id': instance.transaction_id,
                        'order': instance
                    }
                )
                
                # Enroll user in the course
                enrollment, enrolled = Enrollment.objects.get_or_create(
                    user=instance.user,
                    course=course,
                    defaults={
                        'status': 'active',
                        'enrolled_at': timezone.now()
                    }
                )
                
                # Update course enrollment count
                course.enrollment_count = course.enrollments.count()
                course.save(update_fields=['enrollment_count'])
                
            except Course.DoesNotExist:
                # Course not found, skip
                continue