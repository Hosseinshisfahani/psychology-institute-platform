from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from blog.models import Category, Tag, Post, Comment, PostLike, NewsletterSubscription
from tests.models import TestCategory, PsychologicalTest, Question, Choice
from courses.models import CourseCategory, Course, CourseModule, Lesson
from therapy_sessions.models import SessionType, TherapistAvailability, Session
from sales.models import Institution, ServicePackage

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        blog_cat1 = Category.objects.get_or_create(
            name='روانشناسی عمومی',
            slug='general-psychology',
            description='مقالات مربوط به روانشناسی عمومی',
            color='#007bff'
        )[0]
        
        blog_cat2 = Category.objects.get_or_create(
            name='مشاوره خانواده',
            slug='family-counseling',
            description='مقالات مربوط به مشاوره خانواده',
            color='#28a745'
        )[0]
        
        # Create tags
        tag1 = Tag.objects.get_or_create(name='استرس', slug='stress')[0]
        tag2 = Tag.objects.get_or_create(name='اضطراب', slug='anxiety')[0]
        tag3 = Tag.objects.get_or_create(name='خانواده', slug='family')[0]
        
        # Create test categories
        test_cat1 = TestCategory.objects.get_or_create(
            name='شخصیت',
            description='تست‌های شخصیت',
            color='#dc3545'
        )[0]
        
        test_cat2 = TestCategory.objects.get_or_create(
            name='هوش',
            description='تست‌های هوش',
            color='#ffc107'
        )[0]
        
        # Create course categories
        course_cat1 = CourseCategory.objects.get_or_create(
            name='روانشناسی بالینی',
            description='دوره‌های روانشناسی بالینی',
            color='#6f42c1'
        )[0]
        
        course_cat2 = CourseCategory.objects.get_or_create(
            name='مشاوره',
            description='دوره‌های مشاوره',
            color='#fd7e14'
        )[0]
        
        # Create session types
        session_type1 = SessionType.objects.get_or_create(
            name='مشاوره فردی',
            description='جلسات مشاوره فردی',
            duration_minutes=60,
            price=150000
        )[0]
        
        session_type2 = SessionType.objects.get_or_create(
            name='مشاوره خانوادگی',
            description='جلسات مشاوره خانوادگی',
            duration_minutes=90,
            price=200000
        )[0]
        
        # Create service packages
        package1 = ServicePackage.objects.get_or_create(
            name='بسته پایه',
            package_type='basic',
            description='بسته پایه برای موسسات کوچک',
            price=5000000,
            duration_months=12,
            max_users=10,
            max_tests=50,
            max_courses=20,
            max_sessions=100,
            features=['تست‌های پایه', 'دوره‌های مقدماتی', 'گزارش‌گیری ساده']
        )[0]
        
        # Create sample blog posts
        admin_user = User.objects.filter(user_type='admin').first()
        if admin_user:
            post1 = Post.objects.get_or_create(
                title='راه‌های مقابله با استرس',
                slug='stress-management',
                excerpt='در این مقاله راه‌های موثر برای مقابله با استرس را بررسی می‌کنیم.',
                content='استرس یکی از مشکلات شایع در زندگی مدرن است. در این مقاله راه‌های مختلفی برای مدیریت استرس ارائه می‌دهیم...',
                category=blog_cat1,
                author=admin_user,
                status='published',
                is_featured=True
            )[0]
            post1.tags.add(tag1, tag2)
            
            post2 = Post.objects.get_or_create(
                title='نقش خانواده در سلامت روان',
                slug='family-mental-health',
                excerpt='خانواده نقش مهمی در سلامت روان افراد دارد.',
                content='خانواده به عنوان اولین محیط اجتماعی که فرد در آن رشد می‌کند، نقش مهمی در شکل‌گیری شخصیت و سلامت روان دارد...',
                category=blog_cat2,
                author=admin_user,
                status='published'
            )[0]
            post2.tags.add(tag3)
        
        # Create sample tests
        test1 = PsychologicalTest.objects.get_or_create(
            title='تست شخصیت MBTI',
            description='تست شخصیت مایرز-بریگز برای شناخت تیپ شخصیتی شما. این تست به شما کمک می‌کند تا تیپ شخصیتی خود را بهتر بشناسید.',
            category=test_cat1,
            test_type='personality',
            difficulty='medium',
            estimated_duration=30,
            instructions='لطفاً به سوالات با دقت پاسخ دهید. هیچ پاسخ درست یا غلطی وجود ندارد، فقط صادقانه پاسخ دهید.',
            is_free=True,
            created_by=admin_user
        )[0]
        
        test2 = PsychologicalTest.objects.get_or_create(
            title='تست هوش چندگانه',
            description='تست هوش چندگانه گاردنر که انواع مختلف هوش را اندازه‌گیری می‌کند.',
            category=test_cat2,
            test_type='cognitive',
            difficulty='easy',
            estimated_duration=20,
            instructions='این تست انواع مختلف هوش را اندازه‌گیری می‌کند. به سوالات با دقت پاسخ دهید.',
            is_free=False,
            price=50000,
            created_by=admin_user
        )[0]
        
        # Create sample questions for test1 (MBTI)
        from tests.models import Question, Choice
        
        # Question 1
        q1 = Question.objects.get_or_create(
            test=test1,
            question_text='در مهمانی‌ها ترجیح می‌دهید:',
            question_type='single_choice',
            order=1,
            is_required=True
        )[0]
        
        Choice.objects.get_or_create(question=q1, choice_text='با افراد زیادی صحبت کنید', value='E', order=1, score=1)
        Choice.objects.get_or_create(question=q1, choice_text='با چند نفر محدود گفتگو کنید', value='I', order=2, score=1)
        
        # Question 2
        q2 = Question.objects.get_or_create(
            test=test1,
            question_text='در تصمیم‌گیری‌ها بیشتر به چه چیزی توجه می‌کنید:',
            question_type='single_choice',
            order=2,
            is_required=True
        )[0]
        
        Choice.objects.get_or_create(question=q2, choice_text='منطق و واقعیت', value='T', order=1, score=1)
        Choice.objects.get_or_create(question=q2, choice_text='احساسات و ارزش‌ها', value='F', order=2, score=1)
        
        # Question 3
        q3 = Question.objects.get_or_create(
            test=test1,
            question_text='در کارها ترجیح می‌دهید:',
            question_type='single_choice',
            order=3,
            is_required=True
        )[0]
        
        Choice.objects.get_or_create(question=q3, choice_text='برنامه‌ریزی دقیق داشته باشید', value='J', order=1, score=1)
        Choice.objects.get_or_create(question=q3, choice_text='انعطاف‌پذیر باشید', value='P', order=2, score=1)
        
        # Create sample questions for test2 (Multiple Intelligence)
        # Question 1
        q4 = Question.objects.get_or_create(
            test=test2,
            question_text='کدام فعالیت را بیشتر دوست دارید:',
            question_type='single_choice',
            order=1,
            is_required=True
        )[0]
        
        Choice.objects.get_or_create(question=q4, choice_text='خواندن کتاب', value='linguistic', order=1, score=2)
        Choice.objects.get_or_create(question=q4, choice_text='حل کردن پازل', value='logical', order=2, score=2)
        Choice.objects.get_or_create(question=q4, choice_text='نقاشی کردن', value='visual', order=3, score=2)
        Choice.objects.get_or_create(question=q4, choice_text='ورزش کردن', value='kinesthetic', order=4, score=2)
        
        # Question 2
        q5 = Question.objects.get_or_create(
            test=test2,
            question_text='در یادگیری کدام روش برای شما موثرتر است:',
            question_type='single_choice',
            order=2,
            is_required=True
        )[0]
        
        Choice.objects.get_or_create(question=q5, choice_text='گوش دادن به موسیقی', value='musical', order=1, score=2)
        Choice.objects.get_or_create(question=q5, choice_text='کار گروهی', value='interpersonal', order=2, score=2)
        Choice.objects.get_or_create(question=q5, choice_text='کار فردی', value='intrapersonal', order=3, score=2)
        Choice.objects.get_or_create(question=q5, choice_text='مشاهده طبیعت', value='naturalistic', order=4, score=2)
        
        # Create sample courses
        # Create course categories
        course_cat1 = CourseCategory.objects.get_or_create(
            name='روانشناسی بالینی',
            slug='clinical-psychology',
            description='دوره‌های تخصصی روانشناسی بالینی',
            color='#e74c3c',
            icon='fas fa-stethoscope',
            is_active=True
        )[0]
        
        course_cat2 = CourseCategory.objects.get_or_create(
            name='مشاوره خانواده',
            slug='family-counseling',
            description='دوره‌های مشاوره و درمان خانواده',
            color='#3498db',
            icon='fas fa-users',
            is_active=True
        )[0]
        
        course1 = Course.objects.get_or_create(
            title='مقدمه‌ای بر روانشناسی بالینی',
            slug='intro-clinical-psychology',
            description='دوره مقدماتی روانشناسی بالینی که شما را با اصول و مبانی این رشته آشنا می‌کند. این دوره شامل مفاهیم پایه، روش‌های تشخیص و درمان است.',
            short_description='آشنایی با اصول روانشناسی بالینی',
            category=course_cat1,
            instructor=admin_user,
            level='مقدماتی',
            duration_hours=20,
            learning_objectives='آشنایی با اصول روانشناسی بالینی، یادگیری روش‌های تشخیص و درمان',
            prerequisites='هیچ پیش‌نیازی ندارد',
            is_free=True,
            price=0,
            status='published'
        )[0]
        
        course2 = Course.objects.get_or_create(
            title='مشاوره خانواده و زوجین',
            slug='family-couples-counseling',
            description='دوره تخصصی مشاوره خانواده و زوجین که شامل تکنیک‌های درمانی و روش‌های حل تعارض است.',
            short_description='آموزش تکنیک‌های مشاوره خانواده',
            category=course_cat2,
            instructor=admin_user,
            level='متوسط',
            duration_hours=30,
            learning_objectives='یادگیری تکنیک‌های مشاوره خانواده، حل تعارضات زناشویی',
            prerequisites='دوره مقدماتی روانشناسی بالینی',
            is_free=False,
            price=150000,
            status='published'
        )[0]
        
        # Create course modules and lessons
        module1 = CourseModule.objects.get_or_create(
            course=course1,
            title='مفاهیم پایه روانشناسی بالینی',
            description='آشنایی با مفاهیم اساسی',
            order=1,
            is_published=True
        )[0]
        
        Lesson.objects.get_or_create(
            module=module1,
            title='تعریف روانشناسی بالینی',
            description='آشنایی با تعریف و تاریخچه روانشناسی بالینی',
            content='روانشناسی بالینی شاخه‌ای از روانشناسی است که...',
            lesson_type='video',
            duration_minutes=45,
            order=1,
            is_required=True
        )
        
        Lesson.objects.get_or_create(
            module=module1,
            title='روش‌های تشخیص',
            description='آشنایی با روش‌های تشخیص اختلالات روانی',
            content='روش‌های مختلفی برای تشخیص اختلالات روانی وجود دارد...',
            lesson_type='text',
            duration_minutes=60,
            order=2,
            is_required=True
        )
        
        module2 = CourseModule.objects.get_or_create(
            course=course1,
            title='روش‌های درمان',
            description='آشنایی با روش‌های درمانی',
            order=2,
            is_required=True
        )[0]
        
        Lesson.objects.get_or_create(
            module=module2,
            title='درمان شناختی-رفتاری',
            description='آشنایی با CBT',
            content='درمان شناختی-رفتاری یکی از موثرترین روش‌های درمان است...',
            lesson_type='video',
            duration_minutes=50,
            order=1,
            is_required=True
        )
        
        # Create sample institution
        institution1 = Institution.objects.get_or_create(
            name='دانشگاه تهران',
            institution_type='university',
            contact_person='دکتر احمدی',
            email='contact@ut.ac.ir',
            phone='021-61111111',
            address='تهران، خیابان انقلاب',
            city='تهران',
            website='https://ut.ac.ir',
            description='دانشگاه تهران - دانشکده روانشناسی',
            is_verified=True
        )[0]
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
