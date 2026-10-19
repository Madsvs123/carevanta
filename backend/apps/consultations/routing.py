from django.urls import re_path

from .consumers import ConsultationConsumer

websocket_urlpatterns = [
    re_path(r"ws/consultations/(?P<room_id>\w+)/$", ConsultationConsumer.as_asgi()),
]
