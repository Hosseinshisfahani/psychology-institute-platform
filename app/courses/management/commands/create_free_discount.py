from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.courses.models import Coupon
from app.packages.models import PackageCoupon


class Command(BaseCommand):
    help = 'Creates discount codes that make all items free (100% discount)'

    def handle(self, *args, **options):
        # Set validity period - valid for 1 year from now
        valid_from = timezone.now()
        valid_until = valid_from + timedelta(days=365)
        
        # Create course coupon
        course_coupon, created = Coupon.objects.get_or_create(
            code='ALLFREE',
            defaults={
                'title': 'تخفیف ۱۰۰٪ - رایگان',
                'description': 'کد تخفیف رایگان برای همه دوره‌ها',
                'coupon_type': 'percentage',
                'discount_value': 100.00,
                'min_order_amount': 0,
                'max_discount_amount': None,
                'usage_limit': None,  # Unlimited usage
                'used_count': 0,
                'is_active': True,
                'valid_from': valid_from,
                'valid_until': valid_until,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created course coupon: {course_coupon.code}'))
        else:
            # Update existing coupon to ensure it's active and valid
            course_coupon.is_active = True
            course_coupon.valid_from = valid_from
            course_coupon.valid_until = valid_until
            course_coupon.discount_value = 100.00
            course_coupon.save()
            self.stdout.write(self.style.WARNING(f'⟳ Updated existing course coupon: {course_coupon.code}'))
        
        # Create package coupon
        package_coupon, created = PackageCoupon.objects.get_or_create(
            code='ALLFREE',
            defaults={
                'title': 'تخفیف ۱۰۰٪ - رایگان',
                'description': 'کد تخفیف رایگان برای همه پکیج‌ها',
                'coupon_type': 'percentage',
                'discount_value': 100.00,
                'min_order_amount': 0,
                'max_discount_amount': None,
                'usage_limit': None,  # Unlimited usage
                'used_count': 0,
                'is_active': True,
                'valid_from': valid_from,
                'valid_until': valid_until,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created package coupon: {package_coupon.code}'))
        else:
            # Update existing coupon to ensure it's active and valid
            package_coupon.is_active = True
            package_coupon.valid_from = valid_from
            package_coupon.valid_until = valid_until
            package_coupon.discount_value = 100.00
            package_coupon.save()
            self.stdout.write(self.style.WARNING(f'⟳ Updated existing package coupon: {package_coupon.code}'))
        
        self.stdout.write(self.style.SUCCESS('\n═══════════════════════════════════════════════════════'))
        self.stdout.write(self.style.SUCCESS('  Discount Code: ALLFREE'))
        self.stdout.write(self.style.SUCCESS('  Type: 100% Percentage Discount'))
        self.stdout.write(self.style.SUCCESS('  Applies to: All Courses and Packages'))
        self.stdout.write(self.style.SUCCESS('  Usage Limit: Unlimited'))
        self.stdout.write(self.style.SUCCESS(f'  Valid Until: {valid_until.strftime("%Y-%m-%d %H:%M")}'))
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════════════════════\n'))

