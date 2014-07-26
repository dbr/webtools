import time
import datetime
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Periodically refreshes videos"

    def handle(self, *args, **kwargs):
        import ytdl.tasks
        minutes = 20
        while True:
            print "%s Sleeping %s minutes" % (datetime.datetime.now(), minutes)
            time.sleep(60*minutes)

            print "%s Refreshing!" % datetime.datetime.now()
            ytdl.tasks.refresh_all_channels.delay()
