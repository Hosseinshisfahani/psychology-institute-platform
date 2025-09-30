from django.urls import path
from . import api_views

app_name = 'blog_api'

urlpatterns = [
    # Posts
    path('posts/', api_views.PostListView.as_view(), name='post_list'),
    path('posts/<slug:slug>/', api_views.PostDetailView.as_view(), name='post_detail'),
    
    # Categories and Tags
    path('categories/', api_views.CategoryListView.as_view(), name='category_list'),
    path('tags/', api_views.TagListView.as_view(), name='tag_list'),
    
    # Comments
    path('posts/<slug:post_slug>/comments/', api_views.CommentListCreateView.as_view(), name='comment_list_create'),
    
    # Post interactions
    path('posts/<slug:post_slug>/like/', api_views.toggle_post_like, name='post_like'),
    
    # Newsletter
    path('newsletter/subscribe/', api_views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', api_views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
]
