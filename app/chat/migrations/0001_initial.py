# Generated manually for initial chat app migration
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatThread',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('assigned_admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_chat_threads', to=settings.AUTH_USER_MODEL, verbose_name='ادمین مسئول')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_thread', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'گفتگو',
                'verbose_name_plural': 'گفتگوها',
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='پیام')),
                ('is_from_admin', models.BooleanField(default=False, verbose_name='پیام ادمین')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='تاریخ خوانده شدن')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_chat_messages', to=settings.AUTH_USER_MODEL, verbose_name='ارسال کننده')),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatthread', verbose_name='گفتگو')),
            ],
            options={
                'verbose_name': 'پیام',
                'verbose_name_plural': 'پیام‌ها',
                'ordering': ['created_at'],
            },
        ),
    ]
