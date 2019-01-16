from django.core.management.base import BaseCommand, CommandError
from project.api.search import reset_index

class Command(BaseCommand):
    help = 'Resets the elasticsearch index'

    def handle(self, *args, **options):
        reset_index()
        self.stdout.write(self.style.SUCCESS('Successfully reset elasticsearch index'))