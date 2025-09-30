from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Post, Category, Tag, Comment, PostLike, NewsletterSubscription
from .serializers import (
    PostListSerializer, PostDetailSerializer, CategorySerializer,
    TagSerializer, CommentSerializer, PostLikeSerializer, NewsletterSubscriptionSerializer
)


class PostListView(generics.ListAPIView):
    """List all published posts with filtering and search"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
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
        serializer.save(author=self.request.user, post=post)


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
