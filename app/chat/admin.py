from django.contrib import admin

from .models import ChatThread, ChatMessage

'''
@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_admin', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'assigned_admin__email')
    autocomplete_fields = ('user', 'assigned_admin')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('thread', 'sender', 'is_from_admin', 'created_at')
    list_filter = ('is_from_admin', 'created_at')
    search_fields = ('message', 'sender__email', 'thread__user__email')
    autocomplete_fields = ('thread', 'sender')
'''