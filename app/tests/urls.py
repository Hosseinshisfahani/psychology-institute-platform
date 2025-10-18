from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    # Test list and categories
    path('', views.TestListView.as_view(), name='test_list'),
    path('category/<slug:slug>/', views.TestCategoryView.as_view(), name='test_category'),
    
    # Test details and purchase
    path('test/<int:pk>/', views.TestDetailView.as_view(), name='test_detail'),
    path('test/<int:pk>/purchase/', views.TestPurchaseView.as_view(), name='test_purchase'),
    
    # Test session
    path('session/<int:pk>/', views.TestSessionView.as_view(), name='test_session'),
    path('session/<int:pk>/start/', views.TestSessionStartView.as_view(), name='test_session_start'),
    path('session/<int:pk>/question/<int:question_pk>/', views.TestQuestionView.as_view(), name='test_question'),
    path('session/<int:pk>/submit/', views.TestSessionSubmitView.as_view(), name='test_session_submit'),
    
    # Test results
    path('result/<int:pk>/', views.TestResultView.as_view(), name='test_result'),
    path('my-results/', views.UserTestResultsView.as_view(), name='user_test_results'),
    
    # Free tests
    path('free/', views.FreeTestListView.as_view(), name='free_test_list'),
]

