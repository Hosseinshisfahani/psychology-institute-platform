from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Max, Q

from .models import ChatThread, ChatMessage
from .serializers import ChatThreadSerializer, ChatMessageSerializer, ChatMessageCreateSerializer

default_admin_types = {'admin', 'staff'}
User = get_user_model()


def _is_admin(user):
    return getattr(user, 'user_type', None) in default_admin_types


def _get_or_create_thread(user):
    thread, _ = ChatThread.objects.get_or_create(user=user)
    if not thread.assigned_admin:
        admin_user = User.objects.filter(user_type__in=default_admin_types).order_by('id').first()
        if admin_user:
            thread.assigned_admin = admin_user
            thread.save(update_fields=['assigned_admin'])
    return thread


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def thread_detail(request):
    thread = _get_or_create_thread(request.user)
    serializer = ChatThreadSerializer(thread)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    serializer = ChatMessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    thread = _get_or_create_thread(request.user)
    message_text = serializer.validated_data['message'].strip()
    if not message_text:
        return Response({'detail': 'پیام نمی‌تواند خالی باشد.'}, status=status.HTTP_400_BAD_REQUEST)

    message = ChatMessage.objects.create(
        thread=thread,
        sender=request.user,
        message=message_text,
        is_from_admin=request.user.user_type in default_admin_types,
    )

    thread.updated_at = timezone.now()
    thread.save(update_fields=['updated_at'])

    return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_threads(request):
    if not _is_admin(request.user):
        return Response({'detail': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)

    threads = (
        ChatThread.objects.select_related('user', 'assigned_admin')
        .prefetch_related('messages')
        .annotate(
            last_message_at=Max('messages__created_at'),
            unread_count=Count(
                'messages',
                filter=Q(messages__is_from_admin=False, messages__read_at__isnull=True),
            ),
        )
        .order_by('-last_message_at', '-updated_at')
    )

    data = []
    for thread in threads:
        last_message = thread.messages.order_by('-created_at').first()
        data.append({
            'id': thread.id,
            'user_name': thread.user.full_name or thread.user.email,
            'user_email': thread.user.email,
            'assigned_admin_name': thread.assigned_admin.full_name if thread.assigned_admin else None,
            'unread_count': thread.unread_count or 0,
            'last_message_preview': (last_message.message[:80] + '...') if last_message and len(last_message.message) > 80 else (last_message.message if last_message else ''),
            'last_message_at': (thread.last_message_at or thread.updated_at),
        })

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_thread_detail(request, thread_id):
    if not _is_admin(request.user):
        return Response({'detail': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)

    thread = get_object_or_404(ChatThread.objects.select_related('user', 'assigned_admin'), pk=thread_id)

    # Mark user messages as read when admin views the thread
    ChatMessage.objects.filter(
        thread=thread,
        is_from_admin=False,
        read_at__isnull=True,
    ).update(read_at=timezone.now())

    messages = thread.messages.order_by('created_at')
    serialized_messages = ChatMessageSerializer(messages, many=True).data

    data = {
        'id': thread.id,
        'user_name': thread.user.full_name or thread.user.email,
        'user_email': thread.user.email,
        'assigned_admin_name': thread.assigned_admin.full_name if thread.assigned_admin else None,
        'messages': serialized_messages,
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_send_message(request):
    if not _is_admin(request.user):
        return Response({'detail': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ChatMessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    thread_id = serializer.validated_data.get('thread_id')
    if not thread_id:
        return Response({'detail': 'شناسه گفتگو الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

    thread = get_object_or_404(ChatThread, pk=thread_id)

    if thread.assigned_admin is None:
        thread.assigned_admin = request.user
        thread.save(update_fields=['assigned_admin'])

    message_text = serializer.validated_data['message'].strip()
    if not message_text:
        return Response({'detail': 'پیام نمی‌تواند خالی باشد.'}, status=status.HTTP_400_BAD_REQUEST)

    message = ChatMessage.objects.create(
        thread=thread,
        sender=request.user,
        message=message_text,
        is_from_admin=True,
    )

    thread.updated_at = timezone.now()
    thread.save(update_fields=['updated_at'])

    return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)
