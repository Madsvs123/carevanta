import uuid
from django.utils.text import slugify


def generate_reference(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def unique_slug(model, base: str, slug_field: str = "slug") -> str:
    slug = slugify(base)[:200]
    candidate = slug
    idx = 1
    while model.objects.filter(**{slug_field: candidate}).exists():
        candidate = f"{slug}-{idx}"
        idx += 1
    return candidate
