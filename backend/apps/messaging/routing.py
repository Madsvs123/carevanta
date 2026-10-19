from django.urls import re_path

from .consumers import MessagingConsumer

messaging_websocket_urlpatterns = [
    re_path(r"ws/messages/(?P<conversation_id>\d+)/$", MessagingConsumer.as_asgi()),
]
