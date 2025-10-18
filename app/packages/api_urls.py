from django.urls import path
from . import api_views

app_name = 'packages_api'

urlpatterns = [
    # Package list and detail
    path('', api_views.PackageListAPIView.as_view(), name='package_list'),
    path('<slug:slug>/', api_views.PackageDetailAPIView.as_view(), name='package_detail'),
    
    # Categories
    path('categories/', api_views.PackageCategoryListAPIView.as_view(), name='category_list'),
    
    # Purchase
    path('<slug:package_slug>/purchase/', api_views.purchase_package, name='purchase'),
    path('<slug:package_slug>/add-to-cart/', api_views.add_package_to_cart, name='add_to_cart'),
    
    # User packages
    path('my/packages/', api_views.UserPackagesAPIView.as_view(), name='user_packages'),
    path('my/enrollments/', api_views.user_package_enrollments, name='user_enrollments'),
    
    # Progress and courses
    path('<slug:package_slug>/progress/', api_views.package_progress, name='progress'),
    path('<slug:package_slug>/courses/', api_views.package_courses, name='courses'),
    
    # Reviews
    path('<slug:package_slug>/reviews/', api_views.package_reviews, name='reviews'),
    path('<slug:package_slug>/review/', api_views.create_package_review, name='create_review'),
    
    # Coupons
    path('<slug:package_slug>/validate-coupon/', api_views.validate_package_coupon, name='validate_coupon'),
]

