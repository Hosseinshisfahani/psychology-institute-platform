from rest_framework import serializers

from .models import ChatThread, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'is_from_admin', 'created_at', 'sender_name']

    def get_sender_name(self, obj):
        if obj.is_from_admin:
            return obj.sender.full_name or obj.sender.email or 'ادمین'
        return 'شما'


class ChatThreadSerializer(serializers.ModelSerializer):
    assigned_admin_name = serializers.SerializerMethodField()
    messages = ChatMessageSerializer(many=True)

    class Meta:
        model = ChatThread
        fields = ['id', 'assigned_admin_name', 'messages']

    def get_assigned_admin_name(self, obj):
        if obj.assigned_admin:
            return obj.assigned_admin.full_name or obj.assigned_admin.email
        return None


class ChatMessageCreateSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    thread_id = serializers.IntegerField(required=False)
