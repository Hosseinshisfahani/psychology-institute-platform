from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    path('blog/', views.PostListView.as_view(), name='post_list'),
    
    # Post details
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    
    # Categories
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Tags
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # Search
    path('search/', views.PostSearchView.as_view(), name='post_search'),
    
    # Comments
    path('post/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='comment_create'),
    
    # Likes
    path('post/<slug:slug>/like/', views.PostLikeView.as_view(), name='post_like'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
    
    # About founder
    path('about-founder/', views.AboutFounderView.as_view(), name='about_founder'),
    
    # About institute
    path('about-institute/', views.AboutInstituteView.as_view(), name='about_institute'),
]
