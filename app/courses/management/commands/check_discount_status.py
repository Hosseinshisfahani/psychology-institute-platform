from django.core.management.base import BaseCommand
from django.utils import timezone
from app.courses.models import Coupon
from app.packages.models import PackageCoupon


class Command(BaseCommand):
    help = 'Check the status of discount codes'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*70)
        self.stdout.write('                    DISCOUNT CODE STATUS')
        self.stdout.write('='*70 + '\n')
        
        # Check course coupons
        self.stdout.write(self.style.HTTP_INFO('📚 COURSE COUPONS:'))
        self.stdout.write('─'*70)
        
        course_coupons = Coupon.objects.all()
        if course_coupons.exists():
            for coupon in course_coupons:
                self._display_coupon_info(coupon)
        else:
            self.stdout.write('  No course coupons found\n')
        
        # Check package coupons
        self.stdout.write(self.style.HTTP_INFO('📦 PACKAGE COUPONS:'))
        self.stdout.write('─'*70)
        
        package_coupons = PackageCoupon.objects.all()
        if package_coupons.exists():
            for coupon in package_coupons:
                self._display_coupon_info(coupon)
        else:
            self.stdout.write('  No package coupons found\n')
        
        self.stdout.write('='*70 + '\n')
    
    def _display_coupon_info(self, coupon):
        """Display formatted coupon information"""
        now = timezone.now()
        
        # Determine status
        if not coupon.is_active:
            status = self.style.ERROR('INACTIVE')
            status_icon = '✗'
        elif coupon.valid_until < now:
            status = self.style.ERROR('EXPIRED')
            status_icon = '✗'
        elif coupon.valid_from > now:
            status = self.style.WARNING('NOT YET VALID')
            status_icon = '⏱'
        elif coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            status = self.style.ERROR('USAGE LIMIT REACHED')
            status_icon = '✗'
        else:
            status = self.style.SUCCESS('ACTIVE ✓')
            status_icon = '✓'
        
        # Display coupon details
        self.stdout.write(f'\n  {status_icon} Code: {self.style.HTTP_INFO(coupon.code)}')
        self.stdout.write(f'    Title: {coupon.title}')
        self.stdout.write(f'    Type: {coupon.coupon_type}')
        self.stdout.write(f'    Discount: {coupon.discount_value}{"%" if coupon.coupon_type == "percentage" else " Toman"}')
        self.stdout.write(f'    Status: {status}')
        self.stdout.write(f'    Valid from: {coupon.valid_from.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'    Valid until: {coupon.valid_until.strftime("%Y-%m-%d %H:%M")}')
        
        # Usage info
        if coupon.usage_limit:
            usage_pct = (coupon.used_count / coupon.usage_limit) * 100
            self.stdout.write(f'    Usage: {coupon.used_count}/{coupon.usage_limit} ({usage_pct:.1f}%)')
        else:
            self.stdout.write(f'    Usage: {coupon.used_count} (unlimited)')
        
        # Additional info
        if coupon.min_order_amount > 0:
            self.stdout.write(f'    Min. order: {coupon.min_order_amount:,.0f} Toman')
        
        if coupon.max_discount_amount:
            self.stdout.write(f'    Max. discount: {coupon.max_discount_amount:,.0f} Toman')
        
        self.stdout.write('')

