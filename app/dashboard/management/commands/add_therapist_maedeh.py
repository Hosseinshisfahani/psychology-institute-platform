from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings
import os
from pathlib import Path

User = get_user_model()


class Command(BaseCommand):
    help = 'Add or update therapist Maedeh Ahmadi with profile image'

    def handle(self, *args, **options):
        self.stdout.write('Adding/updating therapist Maedeh Ahmadi...')
        
        # Paths to the image files
        base_dir = Path(settings.BASE_DIR)
        profile_image_source = base_dir / 'pedendencies' / 'static' / 'images' / 'therapists' / 'مائده احمدی.jpg'
        info_image = base_dir / 'pedendencies' / 'static' / 'images' / '2_مائده احمدی.jpg'
        
        # Check if profile image exists
        if not profile_image_source.exists():
            self.stdout.write(
                self.style.ERROR(f'Profile image not found: {profile_image_source}')
            )
            return
        
        if not info_image.exists():
            self.stdout.write(
                self.style.WARNING(f'Info image not found: {info_image}')
            )
        
        # Therapist data - update with information from the image
        # Since we can't read the image directly, using existing data structure
        # You may need to update these fields based on the actual image content
        therapist_data = {
            'email': 'maedeh.ahmadi@example.com',
            'first_name': 'مائده',
            'last_name': 'احمدی',
            'user_type': 'therapist',
            'phone_number': '09123456005',
            'specialization': 'کودک',
            'license_number': 'PSY005',
            'experience_years': 5,
            'hourly_rate': 130000,
            'bio': 'کارشناسی ارشد مشاوره و راهنمایی، مدرس دوره های روان شناسی',
            'is_verified': True,
            'is_available': True,
            'gender': 'F',
        }
        
        # Get or create therapist
        therapist, created = User.objects.get_or_create(
            email=therapist_data['email'],
            defaults=therapist_data
        )
        
        if not created:
            # Update existing therapist
            for key, value in therapist_data.items():
                if key != 'email':
                    setattr(therapist, key, value)
        
        # Copy profile image to media directory
        media_profiles_dir = base_dir / 'pedendencies' / 'media' / 'profiles'
        media_profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Destination filename
        profile_image_dest = media_profiles_dir / 'مائده احمدی.jpg'
        
        # Copy the file
        import shutil
        shutil.copy2(profile_image_source, profile_image_dest)
        
        # Set the profile_image field
        # The path should be relative to MEDIA_ROOT
        therapist.profile_image = f'profiles/مائده احمدی.jpg'
        therapist.save()
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} therapist: {therapist.full_name}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Profile image set: {therapist.profile_image.url}'
            )
        )
        
        # Note about updating data from image
        if info_image.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\nNote: Please review the image {info_image} and update the therapist data manually if needed.'
                )
            )


