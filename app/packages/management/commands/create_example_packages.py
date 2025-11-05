from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from app.packages.models import Package, PackageCategory
from app.courses.models import Course, CourseCategory

User = get_user_model()


class Command(BaseCommand):
    help = 'Create example packages with proper data for home page display'

    def handle(self, *args, **options):
        self.stdout.write('Creating example packages...')
        
        # Get or create package category
        category, created = PackageCategory.objects.get_or_create(
            name='بسته‌های جامع روانشناسی',
            defaults={
                'slug': slugify('بسته‌های جامع روانشناسی'),
                'description': 'بسته‌های جامع و کامل برای یادگیری روانشناسی',
                'icon': 'fas fa-brain',
                'color': '#2c5aa0',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created category: {category.name}')
        else:
            self.stdout.write(f'Using existing category: {category.name}')
        
        # Get admin user or create a default instructor
        admin_user = User.objects.filter(user_type='admin').first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        
        # Get or create some courses for the packages (handle multiple categories with same name)
        course_category = CourseCategory.objects.filter(name='روانشناسی بالینی').first()
        if not course_category:
            course_category, _ = CourseCategory.objects.get_or_create(
                slug=slugify('روانشناسی بالینی'),
                defaults={
                    'name': 'روانشناسی بالینی',
                    'description': 'دوره‌های روانشناسی بالینی',
                    'color': '#3498db',
                    'is_active': True
                }
            )
        
        # Create first example package
        package1, created1 = Package.objects.get_or_create(
            slug='baste-psychology-complete',
            defaults={
                'title': 'بسته جامع روانشناسی و مشاوره',
                'short_description': 'بسته کامل شامل دوره‌های تخصصی روانشناسی، مشاوره خانواده، و مهارت‌های درمانی برای تبدیل شدن به یک مشاور حرفه‌ای',
                'description': '''
                این بسته جامع شامل تمام دوره‌های ضروری برای یادگیری روانشناسی و مشاوره است. با خرید این بسته به تمام محتوای آموزشی دسترسی خواهید داشت و می‌توانید به یک مشاور حرفه‌ای تبدیل شوید.

                محتوای بسته شامل:
                - دوره مقدماتی روانشناسی بالینی
                - دوره مشاوره خانواده و زوجین  
                - دوره تکنیک‌های درمان شناختی-رفتاری
                - دوره مهارت‌های ارتباطی در مشاوره
                - دوره مدیریت استرس و اضطراب

                این بسته برای افرادی که می‌خواهند در زمینه روانشناسی و مشاوره فعالیت کنند، مناسب است.
                ''',
                'category': category,
                'status': 'published',
                'is_featured': True,
                'price': 5000000,
                'discount_price': 3500000,
                'duration_months': 6,
                'language': 'fa',
                'learning_objectives': '''
                - آشنایی کامل با اصول روانشناسی بالینی
                - یادگیری تکنیک‌های مشاوره خانواده و زوجین
                - تسلط بر روش‌های درمان شناختی-رفتاری
                - بهبود مهارت‌های ارتباطی و مشاوره
                - یادگیری مدیریت استرس و اضطراب
                ''',
                'prerequisites': 'هیچ پیش‌نیازی لازم نیست، این بسته برای همه مناسب است',
                'published_at': timezone.now(),
                'rating': 4.8,
                'review_count': 45,
                'purchase_count': 120
            }
        )
        
        if created1:
            self.stdout.write(self.style.SUCCESS(f'✓ Created package 1: {package1.title}'))
        else:
            self.stdout.write(f'Package 1 already exists: {package1.title}')
        
        # Create second example package
        package2, created2 = Package.objects.get_or_create(
            slug='baste-personal-growth',
            defaults={
                'title': 'بسته رشد شخصی و بهبود فردی',
                'short_description': 'بسته کامل برای رشد شخصی، بهبود مهارت‌های زندگی، و دستیابی به زندگی بهتر و موفق‌تر',
                'description': '''
                این بسته ویژه برای افرادی است که می‌خواهند زندگی خود را بهبود بخشند و به رشد شخصی دست یابند. شامل دوره‌های کاربردی و عملی برای بهبود کیفیت زندگی است.

                محتوای بسته شامل:
                - دوره مدیریت استرس و اضطراب
                - دوره بهبود اعتماد به نفس
                - دوره مهارت‌های ارتباطی
                - دوره مدیریت زمان و هدف‌گذاری
                - دوره تفکر مثبت و خوشبینی

                این بسته برای همه افراد مناسب است و به شما کمک می‌کند تا زندگی بهتری داشته باشید.
                ''',
                'category': category,
                'status': 'published',
                'is_featured': True,
                'price': 3000000,
                'discount_price': 2000000,
                'duration_months': 4,
                'language': 'fa',
                'learning_objectives': '''
                - یادگیری مدیریت استرس و اضطراب
                - بهبود اعتماد به نفس و خودباوری
                - تقویت مهارت‌های ارتباطی
                - یادگیری مدیریت زمان و هدف‌گذاری
                - توسعه تفکر مثبت و خوشبینی
                ''',
                'prerequisites': 'هیچ پیش‌نیازی لازم نیست',
                'published_at': timezone.now(),
                'rating': 4.9,
                'review_count': 78,
                'purchase_count': 245
            }
        )
        
        if created2:
            self.stdout.write(self.style.SUCCESS(f'✓ Created package 2: {package2.title}'))
        else:
            self.stdout.write(f'Package 2 already exists: {package2.title}')
        
        # Try to add some courses to packages if they exist
        courses = Course.objects.filter(status='published')[:3]
        if courses.exists():
            for course in courses:
                if not package1.courses.filter(id=course.id).exists():
                    package1.courses.add(course)
                if not package2.courses.filter(id=course.id).exists() and courses.count() > 1:
                    package2.courses.add(course)
            self.stdout.write(f'Added {courses.count()} courses to packages')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully created/updated example packages!\n'
                f'  - Package 1: {package1.title}\n'
                f'  - Package 2: {package2.title}\n\n'
                f'Note: Please upload images for these packages through Django admin panel:\n'
                f'  - Go to Packages section in admin\n'
                f'  - Edit each package\n'
                f'  - Upload thumbnail images in the Media section'
            )
        )

