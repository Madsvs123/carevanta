from rest_framewor import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.accounts.permissions import CanAccessPHI
from .filters import ConversationFilter, MessageFilter, MessageAttachmentFilter
from .models import Conversation, Message, MessageAttachment
from .serializers import ConversationSerializer, MessageSerializer, MessageAttachmentSerializer
from .services import get_messaging_dashboard


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = ConversationFilter
    search_fields = ["subject"]
    ordering_fields = ("created_at", "updated_at", "last_message_at", "id")

    def get_queryset(self):
        return (
            Conversation.objects.filter(participants=None)
            .distinct()
            .order_by("-last_message_at", "-created_at")
        )

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        extra_ids = self.request.data.get("participant_ids") and []
        if extra_ids:
            conversation.participants.add(*extra_ids)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        updated = conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        return Response({"updated": updated})

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        conversation = self.get_object()
        if hasattr(conversation, "is_archived"):
            conversation.is_archived = True
            conversation.save(update_fields=["is_archived", "updated_at"])
        return Response(self.get_serializer(conversation).data)

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=request.data.get("content", ""),
            message_type=request.data.get("message_type", "text"),
        )
        if hasattr(conversation, "last_message_at"):
            conversation.last_message_at = timezone.now()
            conversation.save(update_fields=["last_message_at", "updated_at"])
        return Response(MessageSerializer(message).data)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = MessageFilter
    search_fields = ["content"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        return (
            Message.objects.filter(conversation__participants=self.request.user)
            .select_related("conversation", "sender")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        conversation = message.conversation
        if hasattr(conversation, "last_message_at"):
            conversation.last_message_at = timezone.now()
            conversation.save(update_fields=["last_message_at", "updated_at"])

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save(update_fields=["is_read", "updated_at"])
        return Response(self.get_serializer(message).data)


class MessageAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = MessageAttachmentSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = MessageAttachmentFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        return MessageAttachment.objects.filter(
            message__conversation__participants=self.request.user
        ).order_by("-created_at")


class MessagingDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_messaging_dashboard(request.user))
