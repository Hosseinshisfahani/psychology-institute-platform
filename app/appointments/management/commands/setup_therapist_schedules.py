from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.appointments.models import TherapistSchedule, ClinicLocation
from datetime import time

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up basic therapist schedules for all therapists'

    def handle(self, *args, **options):
        self.stdout.write('Setting up therapist schedules...')
        
        # Get the first clinic location
        clinic = ClinicLocation.objects.first()
        if not clinic:
            self.stdout.write(
                self.style.ERROR('No clinic location found. Please run setup_initial_data first.')
            )
            return
        
        # Get all therapists
        therapists = User.objects.filter(user_type='therapist', is_active=True)
        
        if not therapists.exists():
            self.stdout.write(
                self.style.ERROR('No therapists found.')
            )
            return
        
        created_count = 0
        
        # Create schedules for each therapist
        for therapist in therapists:
            # Create schedule for each day of the week (Saturday to Friday)
            for day_of_week in range(7):  # 0=Saturday, 6=Friday
                schedule, created = TherapistSchedule.objects.get_or_create(
                    therapist=therapist,
                    day_of_week=day_of_week,
                    defaults={
                        'start_time': time(9, 0),  # 9:00 AM
                        'end_time': time(18, 0),   # 6:00 PM
                        'location': clinic,
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created schedule for {therapist.full_name} - Day {day_of_week}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Schedule already exists for {therapist.full_name} - Day {day_of_week}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup completed! Created {created_count} new therapist schedules.'
            )
        )
