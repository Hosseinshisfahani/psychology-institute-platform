# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_otpcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name_en',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='نام لاتین'),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name_en',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='نام خانوادگی لاتین'),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'آقای'), ('F', 'خانم')], max_length=1, null=True, verbose_name='جنسیت'),
        ),
    ]

