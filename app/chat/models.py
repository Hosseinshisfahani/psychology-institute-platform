from django.conf import settings
from django.db import models


class ChatThread(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_thread',
        verbose_name='کاربر'
    )
    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_chat_threads',
        verbose_name='ادمین مسئول'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'گفتگو'
        verbose_name_plural = 'گفتگوها'

    def __str__(self):
        return f"گفتگو با {self.user.full_name or self.user.email}"


class ChatMessage(models.Model):
    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='گفتگو'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_chat_messages',
        verbose_name='ارسال کننده'
    )
    message = models.TextField(verbose_name='پیام')
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True, verbose_name='فایل پیوست')
    is_from_admin = models.BooleanField(default=False, verbose_name='پیام ادمین')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ خوانده شدن')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'

    def __str__(self):
        sender = 'ادمین' if self.is_from_admin else 'کاربر'
        return f"{sender} - {self.created_at:%Y/%m/%d %H:%M}"
