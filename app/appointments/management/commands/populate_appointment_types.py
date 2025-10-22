from django.core.management.base import BaseCommand
from app.appointments.models import AppointmentType


class Command(BaseCommand):
    help = 'Populate appointment types with specialization mappings'

    def handle(self, *args, **options):
        # Define appointment types with their specializations
        appointment_types_data = [
            {
                'name': 'مشاوره اضطراب و استرس',
                'description': 'درمان اضطراب و استرس',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['اضطراب و استرس', 'روانشناسی عمومی']
            },
            {
                'name': 'مشاوره اعتیاد',
                'description': 'درمان اعتیاد و وابستگی',
                'default_duration_minutes': 90,
                'price': 200000,
                'specializations': ['اعتیاد', 'روانشناسی عمومی']
            },
            {
                'name': 'مشاوره افسردگی',
                'description': 'درمان افسردگی',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['افسردگی', 'روانشناسی عمومی']
            },
            {
                'name': 'مشاوره خانواده',
                'description': 'درمان مشکلات خانوادگی',
                'default_duration_minutes': 90,
                'price': 200000,
                'specializations': ['خانواده', 'روانشناسی عمومی']
            },
            {
                'name': 'مشاوره زوجین',
                'description': 'درمان مشکلات زناشویی',
                'default_duration_minutes': 90,
                'price': 200000,
                'specializations': ['زوجین', 'خانواده', 'روانشناسی عمومی']
            },
            {
                'name': 'مشاوره شغلی',
                'description': 'راهنمایی شغلی و حرفه‌ای',
                'default_duration_minutes': 60,
                'price': 120000,
                'specializations': ['شغلی', 'روانشناسی عمومی']
            },
            {
                'name': 'مشاوره فردی',
                'description': 'مشاوره فردی عمومی',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['روانشناسی عمومی']
            },
            {
                'name': 'مشاوره کودک و نوجوان',
                'description': 'درمان مشکلات کودکان و نوجوانان',
                'default_duration_minutes': 45,
                'price': 180000,
                'specializations': ['کودک و نوجوان', 'روانشناسی کودک']
            }
        ]

        created_count = 0
        updated_count = 0

        for data in appointment_types_data:
            appointment_type, created = AppointmentType.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'default_duration_minutes': data['default_duration_minutes'],
                    'price': data['price'],
                    'specializations': data['specializations']
                }
            )
            
            if not created:
                # Update existing appointment type with specializations
                appointment_type.specializations = data['specializations']
                appointment_type.save()
                updated_count += 1
            else:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} and updated {updated_count} appointment types with specialization mappings.'
            )
        )
