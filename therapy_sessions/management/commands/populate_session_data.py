from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from therapy_sessions.models import SessionType, TherapistAvailability, Session, SessionRating
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample session types and data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample session data...')
        
        # Create session types
        session_types_data = [
            {
                'name': 'جلسه مشاوره فردی',
                'description': 'جلسه مشاوره فردی برای حل مشکلات شخصی و روانی',
                'duration_minutes': 60,
                'price': 150000,
            },
            {
                'name': 'جلسه مشاوره زوج',
                'description': 'جلسه مشاوره برای زوج‌ها و حل مشکلات رابطه',
                'duration_minutes': 90,
                'price': 200000,
            },
            {
                'name': 'جلسه مشاوره خانواده',
                'description': 'جلسه مشاوره خانوادگی برای حل مشکلات خانوادگی',
                'duration_minutes': 90,
                'price': 180000,
            },
            {
                'name': 'جلسه مشاوره کودک',
                'description': 'جلسه مشاوره تخصصی برای کودکان و نوجوانان',
                'duration_minutes': 45,
                'price': 120000,
            },
            {
                'name': 'جلسه ارزیابی روانی',
                'description': 'جلسه ارزیابی و تشخیص مشکلات روانی',
                'duration_minutes': 120,
                'price': 250000,
            },
        ]
        
        for session_data in session_types_data:
            session_type, created = SessionType.objects.get_or_create(
                name=session_data['name'],
                defaults=session_data
            )
            if created:
                self.stdout.write(f'Created session type: {session_type.name}')
        
        # Get therapists
        therapists = User.objects.filter(user_type='therapist', is_active=True)
        
        if not therapists.exists():
            self.stdout.write(self.style.WARNING('No therapists found. Please create therapists first.'))
            return
        
        # Create therapist availability
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        time_slots = [
            ('09:00', '10:00'),
            ('10:00', '11:00'),
            ('11:00', '12:00'),
            ('14:00', '15:00'),
            ('15:00', '16:00'),
            ('16:00', '17:00'),
            ('17:00', '18:00'),
            ('18:00', '19:00'),
        ]
        
        for therapist in therapists:
            for day in days_of_week:
                # Randomly assign 3-5 time slots per day
                selected_slots = random.sample(time_slots, random.randint(3, 5))
                for start_time, end_time in selected_slots:
                    availability, created = TherapistAvailability.objects.get_or_create(
                        therapist=therapist,
                        day_of_week=day,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'is_available': True
                        }
                    )
                    if created:
                        self.stdout.write(f'Created availability for {therapist.full_name} - {day} {start_time}-{end_time}')
        
        # Create sample sessions
        clients = User.objects.filter(user_type='client', is_active=True)
        session_types = SessionType.objects.filter(is_active=True)
        
        if clients.exists() and session_types.exists():
            # Create past sessions (completed)
            for i in range(10):
                client = random.choice(clients)
                therapist = random.choice(therapists)
                session_type = random.choice(session_types)
                
                # Random date in the past 30 days
                past_date = datetime.now().date() - timedelta(days=random.randint(1, 30))
                past_time = random.choice(['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'])
                
                session = Session.objects.create(
                    client=client,
                    therapist=therapist,
                    session_type=session_type,
                    status='completed',
                    mode=random.choice(['online', 'in_person', 'phone']),
                    scheduled_date=past_date,
                    scheduled_time=past_time,
                    duration_minutes=session_type.duration_minutes,
                    price=session_type.price,
                    is_paid=True,
                    payment_method='online',
                    started_at=datetime.combine(past_date, datetime.strptime(past_time, '%H:%M').time()),
                    ended_at=datetime.combine(past_date, datetime.strptime(past_time, '%H:%M').time()) + timedelta(minutes=session_type.duration_minutes)
                )
                
                # Create rating for some sessions
                if random.choice([True, False]):
                    SessionRating.objects.create(
                        session=session,
                        overall_rating=random.randint(3, 5),
                        therapist_rating=random.randint(3, 5),
                        environment_rating=random.randint(3, 5),
                        helpfulness_rating=random.randint(3, 5),
                        comments='جلسه مفید و رضایت‌بخشی بود.',
                        would_recommend=random.choice([True, False])
                    )
            
            # Create future sessions (scheduled)
            for i in range(5):
                client = random.choice(clients)
                therapist = random.choice(therapists)
                session_type = random.choice(session_types)
                
                # Random date in the future 30 days
                future_date = datetime.now().date() + timedelta(days=random.randint(1, 30))
                future_time = random.choice(['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'])
                
                session = Session.objects.create(
                    client=client,
                    therapist=therapist,
                    session_type=session_type,
                    status=random.choice(['scheduled', 'confirmed']),
                    mode=random.choice(['online', 'in_person', 'phone']),
                    scheduled_date=future_date,
                    scheduled_time=future_time,
                    duration_minutes=session_type.duration_minutes,
                    price=session_type.price,
                    is_paid=random.choice([True, False]),
                    payment_method='online' if random.choice([True, False]) else None
                )
                
                # Generate meeting link for online sessions
                if session.mode == 'online':
                    session.meeting_link = f"https://meet.example.com/{session.id}"
                    session.meeting_id = f"MEET{session.id:06d}"
                    session.meeting_password = "123456"
                    session.save()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample session data')
        )
