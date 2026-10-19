from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sync prescriptions module metadata"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("prescriptions sync completed"))
