from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Sales dashboard
    path('', views.SalesDashboardView.as_view(), name='dashboard'),
    
    # Institutions
    path('institutions/', views.InstitutionListView.as_view(), name='institution_list'),
    path('institution/<int:pk>/', views.InstitutionDetailView.as_view(), name='institution_detail'),
    path('institution/create/', views.InstitutionCreateView.as_view(), name='institution_create'),
    path('institution/<int:pk>/edit/', views.InstitutionEditView.as_view(), name='institution_edit'),
    
    # Service packages
    path('packages/', views.ServicePackageListView.as_view(), name='package_list'),
    path('package/<int:pk>/', views.ServicePackageDetailView.as_view(), name='package_detail'),
    path('package/create/', views.ServicePackageCreateView.as_view(), name='package_create'),
    path('package/<int:pk>/edit/', views.ServicePackageEditView.as_view(), name='package_edit'),
    
    # Subscriptions
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('subscription/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('subscription/create/', views.SubscriptionCreateView.as_view(), name='subscription_create'),
    
    # Orders
    path('orders/', views.InstitutionOrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', views.InstitutionOrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/approve/', views.InstitutionOrderApproveView.as_view(), name='order_approve'),
    path('order/<int:pk>/reject/', views.InstitutionOrderRejectView.as_view(), name='order_reject'),
    
    # Payments
    path('payments/', views.InstitutionPaymentListView.as_view(), name='payment_list'),
    path('payment/<int:pk>/', views.InstitutionPaymentDetailView.as_view(), name='payment_detail'),
    
    # Institution users
    path('institution/<int:institution_pk>/users/', views.InstitutionUserListView.as_view(), name='institution_user_list'),
    path('institution/<int:institution_pk>/user/add/', views.InstitutionUserAddView.as_view(), name='institution_user_add'),
    path('institution-user/<int:pk>/edit/', views.InstitutionUserEditView.as_view(), name='institution_user_edit'),
]

