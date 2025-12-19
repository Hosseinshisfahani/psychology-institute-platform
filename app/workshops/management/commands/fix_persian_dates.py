"""
Management command to fix workshop sessions that have Persian dates stored incorrectly
in the scheduled_datetime field (which should store Gregorian dates).
"""
from django.core.management.base import BaseCommand
from app.workshops.models import WorkshopSession
import jdatetime
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fix workshop sessions with Persian dates stored in scheduled_datetime field'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find sessions with dates that look like Persian dates (year >= 1300)
        # Normal Gregorian dates should be < 1300
        sessions = WorkshopSession.objects.filter(scheduled_datetime__year__gte=1300)
        
        self.stdout.write(f'Found {sessions.count()} sessions with potentially incorrect dates')
        
        fixed_count = 0
        for session in sessions:
            original_date = session.scheduled_datetime
            
            # Check if this looks like a Persian date (year between 1300-1500)
            if 1300 <= original_date.year <= 1500:
                try:
                    # Convert from Persian to Gregorian
                    # The stored date is Persian, so we need to convert it
                    persian_dt = jdatetime.datetime(
                        original_date.year,
                        original_date.month,
                        original_date.day,
                        original_date.hour,
                        original_date.minute,
                        original_date.second
                    )
                    gregorian_dt = persian_dt.togregorian()
                    
                    # Preserve timezone info
                    if timezone.is_aware(original_date):
                        gregorian_dt = timezone.make_aware(gregorian_dt)
                    
                    if dry_run:
                        self.stdout.write(
                            f'Would fix Session {session.id} ({session.title}): '
                            f'{original_date} -> {gregorian_dt}'
                        )
                    else:
                        session.scheduled_datetime = gregorian_dt
                        session.save(update_fields=['scheduled_datetime'])
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Fixed Session {session.id} ({session.title}): '
                                f'{original_date} -> {gregorian_dt}'
                            )
                        )
                    fixed_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error fixing Session {session.id}: {e}'
                        )
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDRY RUN: Would fix {fixed_count} sessions. '
                    f'Run without --dry-run to apply changes.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully fixed {fixed_count} sessions.'
                )
            )
