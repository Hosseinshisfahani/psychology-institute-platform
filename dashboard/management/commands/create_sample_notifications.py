from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dashboard.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample notifications for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample notifications...')
        
        # Get all users
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No users found. Please create users first.'))
            return
        
        # Create sample notifications for each user
        for user in users:
            # Welcome notification
            Notification.objects.get_or_create(
                user=user,
                title='خوش آمدید!',
                message='به مرکز مشاوره و خدمات روانشناسی سرمد خوش آمدید. از خدمات ما لذت ببرید.',
                notification_type='success',
                is_read=False
            )
            
            # Course notification
            Notification.objects.get_or_create(
                user=user,
                title='دوره جدید',
                message='دوره جدید "مقدمه‌ای بر روانشناسی بالینی" منتشر شد.',
                notification_type='info',
                is_read=False
            )
            
            # Test notification
            Notification.objects.get_or_create(
                user=user,
                title='تست جدید',
                message='تست "سنجش هوش هیجانی" آماده انجام است.',
                notification_type='info',
                is_read=True
            )
            
            # Session reminder
            Notification.objects.get_or_create(
                user=user,
                title='یادآوری جلسه',
                message='جلسه درمانی شما فردا ساعت 14:00 برگزار می‌شود.',
                notification_type='warning',
                is_read=False
            )
            
            # Achievement notification
            Notification.objects.get_or_create(
                user=user,
                title='دستاورد جدید',
                message='تبریک! شما اولین دوره خود را تکمیل کردید.',
                notification_type='success',
                is_read=True
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample notifications for {users.count()} users')
        )
