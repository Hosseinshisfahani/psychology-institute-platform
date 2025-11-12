from django.urls import path

from . import api_views

app_name = 'chat_api'

urlpatterns = [
    path('thread/', api_views.thread_detail, name='thread_detail'),
    path('message/', api_views.send_message, name='send_message'),
    path('admin/threads/', api_views.admin_threads, name='admin_threads'),
    path('admin/thread/<int:thread_id>/', api_views.admin_thread_detail, name='admin_thread_detail'),
    path('admin/message/', api_views.admin_send_message, name='admin_send_message'),
]
