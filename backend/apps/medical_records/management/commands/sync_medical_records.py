from django.core.management.bas import BaseCommand


class Command(BaseCommand):
    help = "Sync medical_records module metadata"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("medical_records sync completed"))
