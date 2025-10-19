from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    """Blog categories for organizing content"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='نامک')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code', verbose_name='کد رنگ هگز'))
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class', verbose_name='کلاس آیکون Font Awesome'))
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('دسته‌بندی')
        verbose_name_plural = _('دسته‌بندی‌ها')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Tags for blog posts"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name='نام')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='نامک')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('برچسب')
        verbose_name_plural = _('برچسب‌ها')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    """Blog posts and psychological content"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='نامک')
    excerpt = models.TextField(max_length=500, verbose_name='خلاصه')
    content = models.TextField(verbose_name='محتوای')
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True, verbose_name='تصویر شاخص')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name='دسته‌بندی')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name='برچسب‌ها')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='نویسنده')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='وضعیت')
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    allow_comments = models.BooleanField(default=True, verbose_name='اجازه نظرات')
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    like_count = models.PositiveIntegerField(default=0, verbose_name='تعداد لایک')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انتشار')
    
    class Meta:
        verbose_name = _('پست')
        verbose_name_plural = _('پست‌ها')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    """Comments on blog posts"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='پست')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='نویسنده')
    content = models.TextField(verbose_name='محتوای')
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name='نظر والد')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.full_name} on {self.post.title}"


class PostLike(models.Model):
    """Post likes"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='پست')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes', verbose_name='کاربر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = _('لایک پست')
        verbose_name_plural = _('لایک‌های پست')
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} likes {self.post.title}"


class NewsletterSubscription(models.Model):
    """Newsletter subscriptions"""
    
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ اشتراک')
    unsubscribed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ لغو اشتراک')
    
    class Meta:
        verbose_name = _('اشتراک خبرنامه')
        verbose_name_plural = _('اشتراک‌های خبرنامه')
    
    def __str__(self):
        return self.email