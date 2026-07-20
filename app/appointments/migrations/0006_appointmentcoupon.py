# Generated manually for AppointmentCoupon model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0005_alter_appointment_deposit_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='کد کوپن')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('coupon_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], max_length=20, verbose_name='نوع کوپن')),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='مقدار تخفیف')),
                ('min_order_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='حداقل مبلغ سفارش')),
                ('max_discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='حداکثر مبلغ تخفیف')),
                ('usage_limit', models.PositiveIntegerField(blank=True, null=True, verbose_name='حد استفاده')),
                ('used_count', models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('valid_from', models.DateTimeField(verbose_name='معتبر از')),
                ('valid_until', models.DateTimeField(verbose_name='معتبر تا')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
            ],
            options={
                'verbose_name': 'کوپن نوبت',
                'verbose_name_plural': 'کوپن‌های نوبت',
                'ordering': ['-created_at'],
            },
        ),
    ]

