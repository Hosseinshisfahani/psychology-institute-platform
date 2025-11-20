from rest_framework import serializers

from .models import ChatThread, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'is_from_admin', 'created_at', 'sender_name', 'attachment', 'attachment_name']

    def get_sender_name(self, obj):
        if obj.is_from_admin:
            return obj.sender.full_name or obj.sender.email or 'ادمین'
        return 'شما'

    def get_attachment(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None

    def get_attachment_name(self, obj):
        if obj.attachment:
            return obj.attachment.name.split('/')[-1]
        return None


class ChatThreadSerializer(serializers.ModelSerializer):
    assigned_admin_name = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = ['id', 'assigned_admin_name', 'messages']

    def get_assigned_admin_name(self, obj):
        if obj.assigned_admin:
            return obj.assigned_admin.full_name or obj.assigned_admin.email
        return None

    def get_messages(self, obj):
        messages = obj.messages.order_by('created_at')
        return ChatMessageSerializer(messages, many=True, context=self.context).data


class ChatMessageCreateSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    thread_id = serializers.IntegerField(required=False)
    attachment = serializers.FileField(required=False)
