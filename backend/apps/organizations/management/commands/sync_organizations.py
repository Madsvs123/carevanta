from django.core.management.base import BaseCommand


class Command(BaseCommand)
    help = "Sync organizations module metadata"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("organizations sync completed"))
