from django.urls import path
from . import api_views

app_name = 'workshops_api'

urlpatterns = [
    # Workshop list and detail
    path('', api_views.WorkshopListAPIView.as_view(), name='workshop_list'),
    path('<slug:slug>/', api_views.WorkshopDetailAPIView.as_view(), name='workshop_detail'),
    
    # Categories
    path('categories/', api_views.WorkshopCategoryListAPIView.as_view(), name='category_list'),
    
    # Registration
    path('<slug:workshop_slug>/register/', api_views.register_workshop, name='register'),
    path('<slug:workshop_slug>/complete-payment/', api_views.complete_workshop_payment, name='complete_payment'),
    path('<slug:workshop_slug>/add-to-cart/', api_views.add_workshop_to_cart, name='add_to_cart'),
    
    # User workshops
    path('my/workshops/', api_views.UserWorkshopsAPIView.as_view(), name='user_workshops'),
    
    # Installments
    path('<slug:workshop_slug>/installments/', api_views.workshop_installments, name='installments'),
    
    # Session access
    path('sessions/<int:session_id>/access/', api_views.workshop_session_access, name='session_access'),
    path('sessions/<int:session_id>/attendance/', api_views.mark_session_attendance, name='mark_attendance'),
    
    # Reviews
    path('<slug:workshop_slug>/reviews/', api_views.workshop_reviews, name='reviews'),
    path('<slug:workshop_slug>/review/', api_views.create_workshop_review, name='create_review'),
]

