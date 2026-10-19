from django.db import models


class AppointmentsStatus(models.TextChoices
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    PENDING = "pending", "Pending"
    ARCHIVED = "archived", "Archived"
