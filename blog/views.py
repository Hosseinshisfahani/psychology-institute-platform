from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Post, Category, Tag, Comment, PostLike, NewsletterSubscription


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'blog/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')[:6]
        return context


class PostListView(ListView):
    """List view for blog posts"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['popular_tags'] = Tag.objects.all()[:10]
        return context


class PostDetailView(DetailView):
    """Detail view for individual blog posts"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags', 'comments__author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Increment view count
        post.view_count += 1
        post.save(update_fields=['view_count'])
        
        # Get related posts
        context['related_posts'] = Post.objects.filter(
            status='published',
            category=post.category
        ).exclude(id=post.id)[:3]
        
        return context


class CategoryDetailView(ListView):
    """List view for posts in a specific category"""
    model = Post
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status='published',
            category=self.category
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagDetailView(ListView):
    """List view for posts with a specific tag"""
    model = Post
    template_name = 'blog/tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status='published',
            tags=self.tag
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class PostSearchView(ListView):
    """Search view for blog posts"""
    model = Post
    template_name = 'blog/post_search.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                status='published'
            ).select_related('author', 'category').prefetch_related('tags')
        return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class CommentCreateView(CreateView):
    """Create view for post comments"""
    model = Comment
    fields = ['content']
    template_name = 'blog/comment_form.html'
    
    def form_valid(self, form):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        form.instance.post = post
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده خواهد شد.')
        return response
    
    def get_success_url(self):
        return self.object.post.get_absolute_url()


class PostLikeView(CreateView):
    """View for liking/unliking posts"""
    model = PostLike
    fields = []
    
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, slug=kwargs['slug'])
        user = request.user
        
        if not user.is_authenticated:
            return JsonResponse({'error': 'لطفاً ابتدا وارد شوید'}, status=401)
        
        like, created = PostLike.objects.get_or_create(post=post, user=user)
        
        if not created:
            like.delete()
            post.like_count = max(0, post.like_count - 1)
            liked = False
        else:
            post.like_count += 1
            liked = True
        
        post.save(update_fields=['like_count'])
        
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count
        })


class NewsletterSubscribeView(CreateView):
    """View for newsletter subscription"""
    model = NewsletterSubscription
    fields = ['email']
    template_name = 'blog/newsletter_subscribe.html'
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            messages.success(self.request, 'عضویت شما در خبرنامه با موفقیت انجام شد.')
        else:
            if subscription.is_active:
                messages.info(self.request, 'این ایمیل قبلاً در خبرنامه عضو شده است.')
            else:
                subscription.is_active = True
                subscription.save()
                messages.success(self.request, 'عضویت شما در خبرنامه مجدداً فعال شد.')
        
        return self.render_to_response(self.get_context_data(form=form))


class NewsletterUnsubscribeView(CreateView):
    """View for newsletter unsubscription"""
    model = NewsletterSubscription
    fields = ['email']
    template_name = 'blog/newsletter_unsubscribe.html'
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            subscription.is_active = False
            subscription.unsubscribed_at = timezone.now()
            subscription.save()
            messages.success(self.request, 'عضویت شما در خبرنامه لغو شد.')
        except NewsletterSubscription.DoesNotExist:
            messages.error(self.request, 'این ایمیل در خبرنامه عضو نیست.')
        
        return self.render_to_response(self.get_context_data(form=form))


class AboutFounderView(TemplateView):
    """About founder page view"""
    template_name = 'blog/about_founder.html'


class AboutInstituteView(TemplateView):
    """About institute page view"""
    template_name = 'blog/about_institute.html'