from django.core.management.base import BaseCommand
from app.appointments.models import AppointmentType


class Command(BaseCommand):
    help = 'Create appointment types based on existing therapist specializations'

    def handle(self, *args, **options):
        # Define appointment types based on therapist specializations
        appointment_types_data = [
            # General types (available to all)
            {
                'name': 'مشاوره عمومی',
                'description': 'مشاوره عمومی برای تمام تخصص‌ها',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': []
            },
            {
                'name': 'مشاوره فردی',
                'description': 'مشاوره فردی عمومی',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['روانشناسی عمومی']
            },
            
            # Adult and general psychology
            {
                'name': 'مشاوره بزرگسالان',
                'description': 'مشاوره تخصصی برای بزرگسالان',
                'default_duration_minutes': 60,
                'price': 160000,
                'specializations': ['بزرگسال', 'روانشناسی بالینی']
            },
            {
                'name': 'روانشناسی بالینی',
                'description': 'درمان بالینی و تخصصی',
                'default_duration_minutes': 60,
                'price': 180000,
                'specializations': ['روانشناسی بالینی', 'درمانگر بالینی']
            },
            
            # Schema therapy
            {
                'name': 'طرحواره درمانی',
                'description': 'درمان بر اساس طرحواره‌های شناختی',
                'default_duration_minutes': 90,
                'price': 200000,
                'specializations': ['سوپروایزر طرحواره درمانی', 'طرحواره درمانی']
            },
            
            # Coaching
            {
                'name': 'کوچینگ فردی',
                'description': 'کوچینگ و راهنمایی فردی',
                'default_duration_minutes': 60,
                'price': 170000,
                'specializations': ['کوچینگ فردی', 'کوچینگ']
            },
            
            # Family and couples therapy
            {
                'name': 'مشاوره خانواده',
                'description': 'درمان مشکلات خانوادگی',
                'default_duration_minutes': 90,
                'price': 200000,
                'specializations': ['خانواده', 'خانواده و پیش از ازدواج']
            },
            {
                'name': 'مشاوره زوجین',
                'description': 'درمان مشکلات زناشویی',
                'default_duration_minutes': 90,
                'price': 200000,
                'specializations': ['زوج', 'زوج و پیش از ازدواج']
            },
            {
                'name': 'مشاوره پیش از ازدواج',
                'description': 'راهنمایی و مشاوره پیش از ازدواج',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['پیش از ازدواج', 'خانواده و پیش از ازدواج', 'زوج و پیش از ازدواج']
            },
            
            # Child and adolescent therapy
            {
                'name': 'مشاوره کودک',
                'description': 'درمان مشکلات کودکان',
                'default_duration_minutes': 45,
                'price': 180000,
                'specializations': ['کودک', 'کودک و نوجوان']
            },
            {
                'name': 'مشاوره نوجوانان',
                'description': 'درمان مشکلات نوجوانان',
                'default_duration_minutes': 60,
                'price': 170000,
                'specializations': ['نوجوان و بزرگسال', 'نوجوان و توان بخشی شناختی', 'کودک و نوجوان']
            },
            {
                'name': 'توان‌بخشی شناختی',
                'description': 'توان‌بخشی و بهبود عملکرد شناختی',
                'default_duration_minutes': 60,
                'price': 190000,
                'specializations': ['نوجوان و توان بخشی شناختی', 'توان بخشی شناختی']
            },
            
            # Educational and career counseling
            {
                'name': 'مشاوره تحصیلی',
                'description': 'راهنمایی تحصیلی و آموزشی',
                'default_duration_minutes': 60,
                'price': 140000,
                'specializations': ['تحصیلی']
            },
            {
                'name': 'مشاوره شغلی',
                'description': 'راهنمایی شغلی و حرفه‌ای',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['شغلی و اعتیاد', 'روان شناسی کسب و کار']
            },
            
            # Specialized therapy areas
            {
                'name': 'روانشناسی ورزشی',
                'description': 'مشاوره تخصصی برای ورزشکاران',
                'default_duration_minutes': 60,
                'price': 180000,
                'specializations': ['روان شناسی ورزشی']
            },
            {
                'name': 'مشاوره سلامت روان',
                'description': 'مشاوره تخصصی سلامت روان',
                'default_duration_minutes': 60,
                'price': 160000,
                'specializations': ['سلامت']
            },
            {
                'name': 'درمان اعتیاد',
                'description': 'درمان اعتیاد و وابستگی',
                'default_duration_minutes': 90,
                'price': 200000,
                'specializations': ['شغلی و اعتیاد', 'اعتیاد']
            },
            {
                'name': 'مشاوره جنسی',
                'description': 'درمان مشکلات عملکرد جنسی',
                'default_duration_minutes': 60,
                'price': 180000,
                'specializations': ['مشکلات عملکرد و کارکرد جنسی']
            },
            
            # Business psychology
            {
                'name': 'روانشناسی کسب و کار',
                'description': 'مشاوره تخصصی کسب و کار و سازمانی',
                'default_duration_minutes': 60,
                'price': 170000,
                'specializations': ['روان شناسی کسب و کار']
            },
            
            # Common therapy types
            {
                'name': 'مشاوره اضطراب و استرس',
                'description': 'درمان اضطراب و استرس',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['اضطراب و استرس', 'روانشناسی عمومی']
            },
            {
                'name': 'مشاوره افسردگی',
                'description': 'درمان افسردگی',
                'default_duration_minutes': 60,
                'price': 150000,
                'specializations': ['افسردگی', 'روانشناسی عمومی']
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
                appointment_type.description = data['description']
                appointment_type.default_duration_minutes = data['default_duration_minutes']
                appointment_type.price = data['price']
                appointment_type.specializations = data['specializations']
                appointment_type.save()
                updated_count += 1
            else:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} and updated {updated_count} appointment types based on therapist specializations.'
            )
        )
        
        # Show the mapping
        self.stdout.write('\nAppointment types and their specializations:')
        for apt in AppointmentType.objects.all():
            self.stdout.write(f'- {apt.name}: {apt.specializations}')
