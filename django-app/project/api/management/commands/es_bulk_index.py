from django.core.management.base import BaseCommand, CommandError
from project.api.search import bulk_index

class Command(BaseCommand):
    help = 'Bulk elasticsearch index'

    def handle(self, *args, **options):
        bulk_index()
        self.stdout.write(self.style.SUCCESS('Successfully completed bulk elasticsearch index'))