import django_filters
from .models import Conversation, Message, MessageAttachment

class ConversationFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at, lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Conversation
        fields: list[str] = []

class MessageFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields: list[str] = []

class MessageAttachmentFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = MessageAttachment
        fields: list[str] = []
