from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    """Blog categories for organizing content"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    color = models.CharField(max_length=7, default='#007bff', help_text=_('Hex color code'))
    icon = models.CharField(max_length=50, blank=True, null=True, help_text=_('Font Awesome icon class'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Tags for blog posts"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Name'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('Slug'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
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
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Slug'))
    excerpt = models.TextField(max_length=500, verbose_name=_('Excerpt'))
    content = models.TextField(verbose_name=_('Content'))
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True, verbose_name=_('Featured Image'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name=_('Tags'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Author'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('Status'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))
    allow_comments = models.BooleanField(default=True, verbose_name=_('Allow Comments'))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('View Count'))
    like_count = models.PositiveIntegerField(default=0, verbose_name=_('Like Count'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Published At'))
    
    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
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
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Post'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Author'))
    content = models.TextField(verbose_name=_('Content'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Is Approved'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name=_('Parent Comment'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.full_name} on {self.post.title}"


class PostLike(models.Model):
    """Post likes"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name=_('Post'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes', verbose_name=_('User'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Post Like')
        verbose_name_plural = _('Post Likes')
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} likes {self.post.title}"


class NewsletterSubscription(models.Model):
    """Newsletter subscriptions"""
    
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('Newsletter Subscription')
        verbose_name_plural = _('Newsletter Subscriptions')
    
    def __str__(self):
        return self.email