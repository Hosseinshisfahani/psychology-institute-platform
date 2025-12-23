from rest_framework import serializers
from .models import Post, Category, Tag, Comment, PostLike, NewsletterSubscription


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']


class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    created_at_persian = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featured_image',
            'status', 'view_count', 'like_count',
            'category', 'tags', 'author_name', 'created_at', 'created_at_persian'
        ]
    
    def get_created_at_persian(self, obj):
        from django.utils import timezone
        import jdatetime
        if obj.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jalali_date.strftime('%Y/%m/%d')
        return None


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['updated_at']


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author = serializers.SerializerMethodField()
    created_at_persian = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_name', 'parent', 'created_at', 'created_at_persian', 'is_approved']
        read_only_fields = ['author', 'author_name', 'created_at', 'created_at_persian', 'is_approved']
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'full_name': obj.author.full_name
        }
    
    def get_created_at_persian(self, obj):
        from django.utils import timezone
        import jdatetime
        if obj.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jalali_date.strftime('%Y/%m/%d')
        return None


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post', 'created_at']


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'email', 'is_active', 'created_at']
