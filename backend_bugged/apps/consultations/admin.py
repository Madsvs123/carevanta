from django.contrib import admin

from .models import (
    ConnectionStatusLog,
    Consultation,
    ConsultationFile,
    ConsultationMessage,
    ConsultationNote,
    VirtualWaitingRoom,
)

for model in (
    Consultation,
    VirtualWaitingRoom,
    ConsultationMessage,
    ConsultationNote,
    ConsultationFile,
    ConnectionStatusLog,
):
    admin.site.register(model)
