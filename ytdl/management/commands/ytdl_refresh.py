from django.core.management.base import BaseCommand

from ytdl.tasks import refresh_all_channels


class Command(BaseCommand):
    help = "Check for new videos"

    def handle(self, *args, **kwargs):
        refresh_all_channels(async=False)

