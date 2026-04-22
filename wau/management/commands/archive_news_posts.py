from django.core.management.base import BaseCommand

from wau.models import NewsPost


class Command(BaseCommand):
    help = 'Archive published news posts older than the configured age.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, help='Archive posts older than this many days.')

    def handle(self, *args, **options):
        days = options['days']
        archived_count = NewsPost.archive_stale_posts(days=days)
        self.stdout.write(self.style.SUCCESS(f'Archived {archived_count} news post(s) older than {days} day(s).'))