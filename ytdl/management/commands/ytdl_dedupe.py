import ytdl.models

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Removes videos with duplicate URL's"

    def handle(self, *args, **kwargs):
        kill = '--kill' in args

        if not kill:
            print "Dry-run, specify --kill to delete dupes"

        seen = set()
        for video in ytdl.models.Video.objects.all():
            # TODO: maybe only check for dupes in channel? Utterly unlikely
            url = video.url
            if url in seen:
                print "Dupe %s (%s)" % (url, video.status)
                if kill:
                    video.delete()
            else:
                seen.add(url)
