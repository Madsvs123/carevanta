from django.contrib import admin

from .models import Appointment, AppointmentReminder, WaitingListEntry

admin.site.register(Appointment)
admin.site.register(AppointmentReminder)
admin.site.register(WaitingListEntry)
