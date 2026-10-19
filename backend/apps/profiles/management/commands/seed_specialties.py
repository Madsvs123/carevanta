from django.core.management.base import BaseCommand

from apps.profiles.models import MedicalSpecialty


SPECIALTIES = [
    ("cardiology", "Cardiology", "Heart and cardiovascular system"),
    ("dermatology", "Dermatology", "Skin, hair, and nails"),
    ("endocrinology", "Endocrinology", "Hormones and metabolism"),
    ("family-medicine", "Family Medicine", "Primary care for all ages"),
    ("gastroenterology", "Gastroenterology", "Digestive system"),
    ("neurology", "Neurology", "Brain and nervous system"),
    ("obstetrics-gynecology", "Obstetrics & Gynecology", "Women's health"),
    ("oncology", "Oncology", "Cancer diagnosis and treatment"),
    ("ophthalmology", "Ophthalmology", "Eye care"),
    ("orthopedics", "Orthopedics", "Bones, joints, and muscles"),
    ("pediatrics", "Pediatrics", "Children's health"),
    ("psychiatry", "Psychiatry", "Mental health"),
    ("pulmonology", "Pulmonology", "Lungs and respiratory system"),
    ("urology", "Urology", "Urinary tract and male reproductive system"),
]


class Command(BaseCommand):
    help = "Seed CareVanta with default medical specialties"

    def handle(self, *args, **options):
        created = 0
        for slug, name, description in SPECIALTIES:
            _, was_created = MedicalSpecialty.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "description": description},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} specialties"))
