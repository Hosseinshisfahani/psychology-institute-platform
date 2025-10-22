from django.core.management.base import BaseCommand
from app.appointments.models import ClinicLocation, AppointmentType


class Command(BaseCommand):
    help = 'Set up initial clinic location and appointment types for Sarmad Psychology Institute'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data for Sarmad Psychology Institute...')
        
        # Create Sarmad clinic location
        clinic, created = ClinicLocation.objects.get_or_create(
            name='مرکز مشاوره و خدمات روانشناسی سرمد',
            defaults={
                'address': 'اصفهان، میدان احمد آباد، ابتدای خیابان ولیعصر، جنب بانک مسکن، ساختمان پزشکی، طبقه اول',
                'city': 'اصفهان',
                'phone': '031-32292797',
                'capacity': 5,
                'facilities': {
                    'waiting_room': True,
                    'parking': True,
                    'wheelchair_accessible': True,
                    'wifi': True,
                    'air_conditioning': True
                },
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created clinic: {clinic.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Clinic already exists: {clinic.name}')
            )
        
        # Create appointment types
        appointment_types = [
            {
                'name': 'مشاوره فردی',
                'description': 'جلسه مشاوره فردی با روانشناس متخصص',
                'default_duration_minutes': 60,
                'price': 150000.00,
                'color': '#4CAF50'
            },
            {
                'name': 'مشاوره زوجین',
                'description': 'جلسه مشاوره برای زوجین و حل مشکلات زناشویی',
                'default_duration_minutes': 90,
                'price': 200000.00,
                'color': '#2196F3'
            },
            {
                'name': 'مشاوره خانواده',
                'description': 'جلسه مشاوره خانوادگی برای حل مشکلات خانوادگی',
                'default_duration_minutes': 90,
                'price': 200000.00,
                'color': '#FF9800'
            },
            {
                'name': 'مشاوره کودک و نوجوان',
                'description': 'جلسه مشاوره تخصصی برای کودکان و نوجوانان',
                'default_duration_minutes': 45,
                'price': 120000.00,
                'color': '#9C27B0'
            },
            {
                'name': 'مشاوره اضطراب و استرس',
                'description': 'جلسه تخصصی برای درمان اضطراب و استرس',
                'default_duration_minutes': 60,
                'price': 160000.00,
                'color': '#F44336'
            },
            {
                'name': 'مشاوره افسردگی',
                'description': 'جلسه تخصصی برای درمان افسردگی',
                'default_duration_minutes': 60,
                'price': 160000.00,
                'color': '#607D8B'
            },
            {
                'name': 'مشاوره اعتیاد',
                'description': 'جلسه تخصصی برای درمان اعتیاد و وابستگی',
                'default_duration_minutes': 90,
                'price': 180000.00,
                'color': '#795548'
            },
            {
                'name': 'مشاوره شغلی',
                'description': 'مشاوره برای انتخاب شغل و مسیر شغلی',
                'default_duration_minutes': 60,
                'price': 140000.00,
                'color': '#3F51B5'
            }
        ]
        
        created_count = 0
        for apt_type_data in appointment_types:
            apt_type, created = AppointmentType.objects.get_or_create(
                name=apt_type_data['name'],
                defaults={
                    'description': apt_type_data['description'],
                    'default_duration_minutes': apt_type_data['default_duration_minutes'],
                    'price': apt_type_data['price'],
                    'color': apt_type_data['color'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created appointment type: {apt_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Appointment type already exists: {apt_type.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup completed! Created {created_count} new appointment types.'
            )
        )
