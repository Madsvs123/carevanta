from django.db import models


class SchedulingStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    PENDING = "pending", "Pending"
    ARCHIVED = "archived", "Archived"
