from django.d import models


class OrganizationsStatus(models.TextChoices)
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    PENDING = "pending", "Pending"
    ARCHIVED = "archived", "Archived"
