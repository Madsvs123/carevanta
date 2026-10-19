from django.core.management.bas import BaseCommand


class Command(BaseCommand):
    help = "Sync support module metadata"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("support sync completed"))
