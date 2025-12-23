import logging
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed
from .models import Post, Category, Tag, Comment, PostLike, NewsletterSubscription
from .serializers import (
    PostListSerializer, PostDetailSerializer, CategorySerializer,
    TagSerializer, CommentSerializer, PostLikeSerializer, NewsletterSubscriptionSerializer
)

logger = logging.getLogger(__name__)


class PostListView(generics.ListAPIView):
    """List all published posts with filtering and search"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # We'll add custom pagination
    
    def get_queryset(self):
        try:
            queryset = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
            
            # Search functionality
            search = self.request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | 
                    Q(content__icontains=search) | 
                    Q(excerpt__icontains=search)
                )
            
            # Category filter
            category = self.request.query_params.get('category', None)
            if category:
                queryset = queryset.filter(category__slug=category)
            
            # Tag filter
            tag = self.request.query_params.get('tag', None)
            if tag:
                queryset = queryset.filter(tags__slug=tag)
            
            return queryset.order_by('-created_at')
        except Exception as e:
            logger.error(f"Error in PostListView.get_queryset: {str(e)}", exc_info=True)
            # Return empty queryset on error
            return Post.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Handle limit parameter (used for simple limiting without pagination)
            limit = request.query_params.get('limit')
            if limit:
                try:
                    limit = int(limit)
                    posts = queryset[:limit]
                    serializer = self.get_serializer(posts, many=True)
                    return Response({
                        'results': serializer.data,
                        'count': len(serializer.data)
                    })
                except ValueError:
                    pass  # If limit is not a valid integer, fall through to pagination
            
            # Custom pagination
            page_size = int(request.query_params.get('page_size', 12))
            page = int(request.query_params.get('page', 1))
            
            start = (page - 1) * page_size
            end = start + page_size
            
            posts = queryset[start:end]
            total_count = queryset.count()
            
            serializer = self.get_serializer(posts, many=True)
            
            return Response({
                'results': serializer.data,
                'count': total_count,
                'next': f"?page={page + 1}&page_size={page_size}" if end < total_count else None,
                'previous': f"?page={page - 1}&page_size={page_size}" if page > 1 else None,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            })
        except Exception as e:
            logger.error(f"Error in PostListView: {str(e)}", exc_info=True)
            return Response({
                'error': 'An error occurred while fetching posts',
                'results': [],
                'count': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostDetailView(generics.RetrieveAPIView):
    """Get a single post by slug"""
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryListView(generics.ListAPIView):
    """List all categories"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by('name')


class TagListView(generics.ListAPIView):
    """List all tags"""
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Tag.objects.all().order_by('name')


class CommentListCreateView(generics.ListCreateAPIView):
    """List and create comments for a post"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        post_slug = self.kwargs.get('post_slug')
        post = get_object_or_404(Post, slug=post_slug, status='published')
        return Comment.objects.filter(post=post, is_approved=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        post_slug = self.kwargs.get('post_slug')
        post = get_object_or_404(Post, slug=post_slug, status='published')
        parent = serializer.validated_data.get('parent')
        
        # Validate that parent comment belongs to the same post
        if parent and parent.post != post:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'parent': 'Parent comment must belong to the same post.'})
        
        serializer.save(author=self.request.user, post=post, parent=parent)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_post_like(request, post_slug):
    """Toggle like for a post"""
    post = get_object_or_404(Post, slug=post_slug, status='published')
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    # Update like count
    post.like_count = PostLike.objects.filter(post=post).count()
    post.save(update_fields=['like_count'])
    
    return Response({
        'liked': liked,
        'like_count': post.like_count
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def newsletter_subscribe(request):
    """Subscribe to newsletter"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    subscription, created = NewsletterSubscription.objects.get_or_create(
        email=email,
        defaults={'is_active': True}
    )
    
    if not created and subscription.is_active:
        return Response({'message': 'Already subscribed'}, status=status.HTTP_200_OK)
    
    subscription.is_active = True
    subscription.save()
    
    return Response({'message': 'Successfully subscribed'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def newsletter_unsubscribe(request):
    """Unsubscribe from newsletter"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        subscription = NewsletterSubscription.objects.get(email=email)
        subscription.is_active = False
        subscription.save()
        return Response({'message': 'Successfully unsubscribed'}, status=status.HTTP_200_OK)
    except NewsletterSubscription.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)


# RSS Feed
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def blog_rss_feed(request):
    """RSS feed for blog posts"""
    posts = Post.objects.filter(status='published').order_by('-published_at')[:20]
    
    feed = Rss201rev2Feed(
        title="مرکز مشاوره و خدمات روانشناسی سرمد - بلاگ",
        link=request.build_absolute_uri('/blog/'),
        description="آخرین مقالات و مطالب روانشناسی",
        language='fa'
    )
    
    for post in posts:
        feed.add_item(
            title=post.title,
            link=request.build_absolute_uri(post.get_absolute_url()),
            description=post.excerpt,
            pubdate=post.published_at or post.created_at,
            author_name=post.author.full_name,
        )
    
    response = HttpResponse(feed.writeString('utf-8'), content_type='application/rss+xml; charset=utf-8')
    return response


# Sitemap
class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Post.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def blog_sitemap(request):
    """Generate sitemap for blog posts"""
    posts = Post.objects.filter(status='published')
    
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for post in posts:
        sitemap_content += f'  <url>\n'
        sitemap_content += f'    <loc>{request.build_absolute_uri(post.get_absolute_url())}</loc>\n'
        sitemap_content += f'    <lastmod>{post.updated_at.strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_content += f'    <changefreq>weekly</changefreq>\n'
        sitemap_content += f'    <priority>0.8</priority>\n'
        sitemap_content += f'  </url>\n'
    
    sitemap_content += '</urlset>'
    
    response = HttpResponse(sitemap_content, content_type='application/xml')
    return response
