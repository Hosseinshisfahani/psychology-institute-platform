from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from admin_panel.models import AdminDashboard, AdminWidget, AdminNotification, AdminSetting
from payment.models import PaymentMethod

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate admin panel with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating admin panel sample data...')

        # Create admin dashboard
        dashboard, created = AdminDashboard.objects.get_or_create(
            title='پنل مدیریت اصلی',
            defaults={
                'description': 'پنل مدیریت اصلی سیستم روانشناسی',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created admin dashboard')
            )

        # Create payment methods
        payment_methods = [
            {
                'name': 'زرین‌پال',
                'payment_type': 'zarinpal',
                'is_active': True,
                'config': {
                    'merchant_id': 'test_merchant_id',
                    'callback_url': 'https://example.com/payment/callback/',
                    'description': 'پرداخت آنلاین با زرین‌پال'
                }
            },
            {
                'name': 'انتقال بانکی',
                'payment_type': 'bank_transfer',
                'is_active': True,
                'config': {
                    'bank_name': 'بانک ملی',
                    'account_number': '1234567890',
                    'description': 'انتقال وجه به حساب بانکی'
                }
            }
        ]

        for method_data in payment_methods:
            method, created = PaymentMethod.objects.get_or_create(
                name=method_data['name'],
                defaults=method_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created payment method: {method.name}')
                )

        # Create admin settings
        settings_data = [
            {
                'key': 'site_name',
                'value': 'مرکز مشاوره و خدمات روانشناسی سرمد',
                'setting_type': 'general',
                'description': 'نام سایت'
            },
            {
                'key': 'site_description',
                'value': 'مرکز تخصصی مشاوره و خدمات روانشناسی',
                'setting_type': 'general',
                'description': 'توضیحات سایت'
            },
            {
                'key': 'contact_email',
                'value': 'info@psychology-institute.com',
                'setting_type': 'general',
                'description': 'ایمیل تماس'
            },
            {
                'key': 'contact_phone',
                'value': '021-12345678',
                'setting_type': 'general',
                'description': 'شماره تماس'
            },
            {
                'key': 'max_login_attempts',
                'value': '5',
                'setting_type': 'security',
                'description': 'حداکثر تلاش برای ورود'
            },
            {
                'key': 'session_timeout',
                'value': '3600',
                'setting_type': 'security',
                'description': 'زمان انقضای جلسه (ثانیه)'
            },
            {
                'key': 'smtp_host',
                'value': 'smtp.gmail.com',
                'setting_type': 'email',
                'description': 'سرور SMTP'
            },
            {
                'key': 'smtp_port',
                'value': '587',
                'setting_type': 'email',
                'description': 'پورت SMTP'
            },
            {
                'key': 'backup_frequency',
                'value': 'daily',
                'setting_type': 'backup',
                'description': 'فرکانس پشتیبان‌گیری'
            }
        ]

        for setting_data in settings_data:
            setting, created = AdminSetting.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created setting: {setting.key}')
                )

        # Create sample notifications
        notifications_data = [
            {
                'title': 'خوش آمدید به پنل مدیریت',
                'message': 'به پنل مدیریت مرکز روانشناسی سرمد خوش آمدید. از امکانات این پنل برای مدیریت بهتر سیستم استفاده کنید.',
                'notification_type': 'info',
                'is_global': True
            },
            {
                'title': 'به‌روزرسانی سیستم',
                'message': 'سیستم به آخرین نسخه به‌روزرسانی شد. لطفاً در صورت بروز مشکل با تیم پشتیبانی تماس بگیرید.',
                'notification_type': 'success',
                'is_global': True
            },
            {
                'title': 'پشتیبان‌گیری خودکار',
                'message': 'پشتیبان‌گیری خودکار روزانه با موفقیت انجام شد.',
                'notification_type': 'info',
                'is_global': True
            }
        ]

        for notification_data in notifications_data:
            notification, created = AdminNotification.objects.get_or_create(
                title=notification_data['title'],
                defaults=notification_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created notification: {notification.title}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated admin panel data!')
        )

