# Generated migration for appointments app
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام اتاق')),
                ('room_number', models.CharField(max_length=20, unique=True, verbose_name='شماره اتاق')),
                ('floor', models.IntegerField(verbose_name='طبقه')),
                ('capacity', models.PositiveIntegerField(default=2, verbose_name='ظرفیت')),
                ('facilities', models.TextField(blank=True, verbose_name='امکانات', help_text='امکانات موجود در اتاق')),
                ('is_available', models.BooleanField(default=True, verbose_name='در دسترس')),
                ('notes', models.TextField(blank=True, verbose_name='یادداشت‌ها')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
            ],
            options={
                'verbose_name': 'اتاق ملاقات',
                'verbose_name_plural': 'اتاق‌های ملاقات',
                'ordering': ['floor', 'room_number'],
            },
        ),
        migrations.CreateModel(
            name='AppointmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام نوع ملاقات')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('duration_minutes', models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='هزینه')),
                ('requires_preparation', models.BooleanField(default=False, verbose_name='نیاز به آمادگی قبلی')),
                ('preparation_instructions', models.TextField(blank=True, null=True, verbose_name='دستورالعمل آمادگی')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('max_advance_booking_days', models.PositiveIntegerField(default=30, verbose_name='حداکثر روز رزرو از قبل')),
                ('min_advance_booking_hours', models.PositiveIntegerField(default=24, verbose_name='حداقل ساعت رزرو از قبل')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
            ],
            options={
                'verbose_name': 'نوع ملاقات',
                'verbose_name_plural': 'انواع ملاقات',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('counselor', 'مشاور'), ('psychologist', 'روانشناس'), ('psychiatrist', 'روانپزشک'), ('registrar', 'کارشناس پذیرش'), ('director', 'مدیر'), ('other', 'سایر')], max_length=50, verbose_name='نقش')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='عنوان شغلی')),
                ('bio', models.TextField(blank=True, null=True, verbose_name='بیوگرافی')),
                ('specializations', models.TextField(blank=True, null=True, verbose_name='تخصص‌ها', help_text='تخصص‌ها را با کاما جدا کنید')),
                ('room_number', models.CharField(blank=True, max_length=50, verbose_name='شماره اتاق')),
                ('phone_extension', models.CharField(blank=True, max_length=20, verbose_name='داخلی تلفن')),
                ('is_available', models.BooleanField(default=True, verbose_name='در دسترس')),
                ('accepts_appointments', models.BooleanField(default=True, verbose_name='پذیرش وقت ملاقات')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='staff_profiles/', verbose_name='تصویر پروفایل')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='staff_profile', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'کارمند',
                'verbose_name_plural': 'کارمندان',
                'ordering': ['user__first_name', 'user__last_name'],
            },
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='تاریخ')),
                ('start_time', models.TimeField(verbose_name='زمان شروع')),
                ('end_time', models.TimeField(verbose_name='زمان پایان')),
                ('is_available', models.BooleanField(default=True, verbose_name='در دسترس')),
                ('is_booked', models.BooleanField(default=False, verbose_name='رزرو شده')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('appointment_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='appointments.appointmenttype', verbose_name='نوع ملاقات')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_slots', to='appointments.staff', verbose_name='کارمند')),
            ],
            options={
                'verbose_name': 'بازه زمانی',
                'verbose_name_plural': 'بازه‌های زمانی',
                'ordering': ['date', 'start_time'],
                'unique_together': {('staff', 'date', 'start_time')},
            },
        ),
        migrations.CreateModel(
            name='StaffAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'شنبه'), (1, 'یکشنبه'), (2, 'دوشنبه'), (3, 'سه‌شنبه'), (4, 'چهارشنبه'), (5, 'پنج‌شنبه'), (6, 'جمعه')], verbose_name='روز هفته')),
                ('start_time', models.TimeField(verbose_name='زمان شروع')),
                ('end_time', models.TimeField(verbose_name='زمان پایان')),
                ('is_available', models.BooleanField(default=True, verbose_name='در دسترس')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('appointment_types', models.ManyToManyField(to='appointments.appointmenttype', verbose_name='انواع ملاقات قابل ارائه')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability', to='appointments.staff', verbose_name='کارمند')),
            ],
            options={
                'verbose_name': 'برنامه حضور کارمند',
                'verbose_name_plural': 'برنامه‌های حضور کارمندان',
                'ordering': ['staff', 'day_of_week', 'start_time'],
                'unique_together': {('staff', 'day_of_week', 'start_time')},
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'در انتظار تایید'), ('confirmed', 'تایید شده'), ('completed', 'انجام شده'), ('cancelled', 'لغو شده'), ('no_show', 'عدم حضور')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('date', models.DateField(verbose_name='تاریخ')),
                ('start_time', models.TimeField(verbose_name='زمان شروع')),
                ('end_time', models.TimeField(verbose_name='زمان پایان')),
                ('purpose', models.TextField(verbose_name='هدف ملاقات')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')),
                ('internal_notes', models.TextField(blank=True, null=True, verbose_name='یادداشت‌های داخلی', help_text='فقط قابل مشاهده توسط کارمندان')),
                ('phone_number', models.CharField(max_length=20, verbose_name='شماره تماس')),
                ('alternative_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='شماره تماس جایگزین')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='هزینه')),
                ('is_paid', models.BooleanField(default=False, verbose_name='پرداخت شده')),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True, verbose_name='روش پرداخت')),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='شناسه تراکنش')),
                ('confirmed_at', models.DateTimeField(blank=True, null=True, verbose_name='تایید شده در')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='انجام شده در')),
                ('arrival_time', models.TimeField(blank=True, null=True, verbose_name='زمان حضور')),
                ('departure_time', models.TimeField(blank=True, null=True, verbose_name='زمان خروج')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('appointment_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='appointments.appointmenttype', verbose_name='نوع ملاقات')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to=settings.AUTH_USER_MODEL, verbose_name='مراجع')),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='confirmed_appointments', to=settings.AUTH_USER_MODEL, verbose_name='تایید شده توسط')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to='appointments.appointmentroom', verbose_name='اتاق')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='appointments.staff', verbose_name='کارمند')),
                ('time_slot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment', to='appointments.timeslot', verbose_name='بازه زمانی')),
            ],
            options={
                'verbose_name': 'وقت ملاقات',
                'verbose_name_plural': 'وقت‌های ملاقات',
                'ordering': ['-date', '-start_time'],
            },
        ),
        migrations.CreateModel(
            name='AppointmentReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reminder_type', models.CharField(choices=[('sms', 'پیامک'), ('email', 'ایمیل'), ('call', 'تماس تلفنی')], max_length=20, verbose_name='نوع یادآوری')),
                ('scheduled_time', models.DateTimeField(verbose_name='زمان برنامه‌ریزی شده')),
                ('is_sent', models.BooleanField(default=False, verbose_name='ارسال شده')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='ارسال شده در')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='appointments.appointment', verbose_name='وقت ملاقات')),
            ],
            options={
                'verbose_name': 'یادآوری ملاقات',
                'verbose_name_plural': 'یادآوری‌های ملاقات',
                'ordering': ['scheduled_time'],
            },
        ),
        migrations.CreateModel(
            name='AppointmentFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overall_rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='امتیاز کلی')),
                ('staff_rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='امتیاز کارمند')),
                ('facility_rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='امتیاز محیط')),
                ('waiting_time_rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='امتیاز زمان انتظار')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='نظرات')),
                ('would_recommend', models.BooleanField(default=True, verbose_name='توصیه می‌کند')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='appointments.appointment', verbose_name='وقت ملاقات')),
            ],
            options={
                'verbose_name': 'بازخورد ملاقات',
                'verbose_name_plural': 'بازخوردهای ملاقات',
            },
        ),
        migrations.CreateModel(
            name='AppointmentCancellation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('client_request', 'درخواست مراجع'), ('staff_request', 'درخواست کارمند'), ('emergency', 'اضطراری'), ('institute_closed', 'تعطیلی موسسه'), ('other', 'سایر')], max_length=20, verbose_name='دلیل')),
                ('explanation', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('cancelled_at', models.DateTimeField(auto_now_add=True, verbose_name='لغو شده در')),
                ('refund_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='مبلغ بازگشت')),
                ('is_refunded', models.BooleanField(default=False, verbose_name='بازگشت داده شده')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cancellations', to='appointments.appointment', verbose_name='وقت ملاقات')),
                ('cancelled_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_cancellations', to=settings.AUTH_USER_MODEL, verbose_name='لغو شده توسط')),
            ],
            options={
                'verbose_name': 'لغو ملاقات',
                'verbose_name_plural': 'لغوهای ملاقات',
                'ordering': ['-cancelled_at'],
            },
        ),
    ]