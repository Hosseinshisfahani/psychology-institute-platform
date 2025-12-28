# Generated manually for wallet system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_cartitem_metadata_orderitem_metadata'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='موجودی')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'کیف پول',
                'verbose_name_plural': 'کیف پول‌ها',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('refund', 'بازگشت وجه'), ('purchase', 'خرید'), ('admin_adjustment', 'تغییر دستی')], max_length=20, verbose_name='نوع تراکنش')),
                ('amount', models.DecimalField(decimal_places=2, help_text='مثبت برای افزودن، منفی برای کسر', max_digits=10, verbose_name='مبلغ')),
                ('balance_after', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='موجودی پس از تراکنش')),
                ('reference_id', models.PositiveIntegerField(blank=True, help_text='شناسه سفارش، نوبت یا تراکنش مرتبط', null=True, verbose_name='شناسه مرجع')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='payment.wallet', verbose_name='کیف پول')),
            ],
            options={
                'verbose_name': 'تراکنش کیف پول',
                'verbose_name_plural': 'تراکنش‌های کیف پول',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['wallet', '-created_at'], name='payment_wal_wallet__idx'),
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['transaction_type'], name='payment_wal_transac_idx'),
        ),
    ]

