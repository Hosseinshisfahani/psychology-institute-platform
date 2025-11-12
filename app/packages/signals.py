from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.payment.models import Order

from .models import Package, PackageProgress, PackagePurchase


@receiver(post_save, sender=Order)
def handle_package_purchase(sender, instance, created, **kwargs):
    """
    Ensure users gain access to all courses included in purchased packages
    once an order payment is completed.
    """
    if instance.status != 'paid' or instance.payment_status != 'completed':
        return

    package_items = instance.items.filter(item_type='package')
    if not package_items.exists():
        return

    payment_method_name = (
        instance.payment_method.name if instance.payment_method else 'unknown'
    )

    for item in package_items:
        try:
            package = Package.objects.get(id=item.item_id)
        except Package.DoesNotExist:
            continue

        purchase_defaults = {
            'amount_paid': item.total_price,
            'original_price': package.price,
            'discount_amount': max(package.price - item.unit_price, 0),
            'payment_method': payment_method_name,
            'transaction_id': instance.transaction_id,
            'order': instance,
        }

        purchase, was_created = PackagePurchase.objects.get_or_create(
            user=instance.user,
            package=package,
            defaults=purchase_defaults,
        )

        if not was_created:
            fields_to_update = []

            if purchase.amount_paid != item.total_price:
                purchase.amount_paid = item.total_price
                fields_to_update.append('amount_paid')

            new_discount_amount = max(package.price - item.unit_price, 0)
            if purchase.discount_amount != new_discount_amount:
                purchase.discount_amount = new_discount_amount
                fields_to_update.append('discount_amount')

            if purchase.payment_method != payment_method_name:
                purchase.payment_method = payment_method_name
                fields_to_update.append('payment_method')

            if (
                instance.transaction_id
                and purchase.transaction_id != instance.transaction_id
            ):
                purchase.transaction_id = instance.transaction_id
                fields_to_update.append('transaction_id')

            if purchase.order_id != instance.id:
                purchase.order = instance
                fields_to_update.append('order')

            if fields_to_update:
                purchase.save(update_fields=fields_to_update)

        purchase.create_course_enrollments()
        PackageProgress.objects.get_or_create(purchase=purchase)

        if was_created:
            Package.objects.filter(id=package.id).update(
                purchase_count=F('purchase_count') + 1
            )

