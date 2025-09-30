from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample users for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample users...')
        
        # Create therapist users
        therapists_data = [
            {
                'email': 'dr.ahmadi@example.com',
                'first_name': 'دکتر',
                'last_name': 'احمدی',
                'user_type': 'therapist',
                'phone_number': '09123456789',
                'specialization': 'روانشناسی بالینی',
                'license_number': 'PSY001',
                'experience_years': 8,
                'hourly_rate': 180000,
                'bio': 'متخصص روانشناسی بالینی با 8 سال تجربه در درمان اختلالات اضطرابی و افسردگی.',
                'is_verified': True,
                'is_available': True,
            },
            {
                'email': 'dr.mohammadi@example.com',
                'first_name': 'دکتر',
                'last_name': 'محمدی',
                'user_type': 'therapist',
                'phone_number': '09123456790',
                'specialization': 'روانشناسی خانواده',
                'license_number': 'PSY002',
                'experience_years': 12,
                'hourly_rate': 200000,
                'bio': 'متخصص روانشناسی خانواده با 12 سال تجربه در مشاوره زوج و خانواده.',
                'is_verified': True,
                'is_available': True,
            },
            {
                'email': 'dr.karimi@example.com',
                'first_name': 'دکتر',
                'last_name': 'کریمی',
                'user_type': 'therapist',
                'phone_number': '09123456791',
                'specialization': 'روانشناسی کودک',
                'license_number': 'PSY003',
                'experience_years': 6,
                'hourly_rate': 150000,
                'bio': 'متخصص روانشناسی کودک و نوجوان با 6 سال تجربه در درمان مشکلات رفتاری کودکان.',
                'is_verified': True,
                'is_available': True,
            },
            {
                'email': 'dr.nasiri@example.com',
                'first_name': 'دکتر',
                'last_name': 'نصیری',
                'user_type': 'therapist',
                'phone_number': '09123456792',
                'specialization': 'روانشناسی زوج',
                'license_number': 'PSY004',
                'experience_years': 10,
                'hourly_rate': 190000,
                'bio': 'متخصص روانشناسی زوج با 10 سال تجربه در مشاوره روابط زناشویی.',
                'is_verified': True,
                'is_available': False,
            },
        ]
        
        for therapist_data in therapists_data:
            user, created = User.objects.get_or_create(
                email=therapist_data['email'],
                defaults=therapist_data
            )
            if created:
                user.username = therapist_data['email']  # Set username to email
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created therapist: {user.full_name}')
        
        # Create client users
        clients_data = [
            {
                'email': 'client1@example.com',
                'first_name': 'علی',
                'last_name': 'رضایی',
                'user_type': 'client',
                'phone_number': '09123456793',
                'bio': 'علاقه‌مند به بهبود وضعیت روانی و رشد شخصی.',
                'is_verified': True,
            },
            {
                'email': 'client2@example.com',
                'first_name': 'فاطمه',
                'last_name': 'احمدی',
                'user_type': 'client',
                'phone_number': '09123456794',
                'bio': 'به دنبال مشاوره برای حل مشکلات خانوادگی.',
                'is_verified': True,
            },
            {
                'email': 'client3@example.com',
                'first_name': 'محمد',
                'last_name': 'حسینی',
                'user_type': 'client',
                'phone_number': '09123456795',
                'bio': 'نیاز به مشاوره برای مشکلات شغلی و استرس.',
                'is_verified': True,
            },
        ]
        
        for client_data in clients_data:
            user, created = User.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            if created:
                user.username = client_data['email']  # Set username to email
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created client: {user.full_name}')
        
        # Create admin user
        admin_data = {
            'email': 'admin@example.com',
            'first_name': 'مدیر',
            'last_name': 'سیستم',
            'user_type': 'admin',
            'phone_number': '09123456796',
            'is_verified': True,
            'is_staff': True,
            'is_superuser': True,
        }
        
        admin_user, created = User.objects.get_or_create(
            email=admin_data['email'],
            defaults=admin_data
        )
        if created:
            admin_user.username = admin_data['email']  # Set username to email
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin: {admin_user.full_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample users')
        )
