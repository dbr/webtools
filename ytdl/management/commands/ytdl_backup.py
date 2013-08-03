import os
import sys
import json

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Backups the status of videos"

    def handle(self, *args, **kwargs):
        if len(args) == 1:
            output_file = args[0]
            f = open(output_file +  ".tmp", "w+")
        elif len(args) == 0:
            f = sys.stdout
        else:
            raise CommandError("First argument is output file. If unspecified, writes to stdout")


        import ytdl.models

        channels = []
        for c in ytdl.models.Channel.objects.all():
            chaninfo = {'chanid': c.chanid,
                        'service': c.service,
                        'videos': []
                    }
            for v in ytdl.models.Video.objects.filter(channel = c):
                chaninfo['videos'].append(
                    {'title': v.title,
                     'url': v.url,
                     'videoid': v.videoid,
                     'status': v.status,
                     'publishdate': v.status,
                     'service': c.service,
                 })

            channels.append(chaninfo)

        json.dump(channels, f,
                  sort_keys=True, indent=1, separators=(',', ': '))
        f.write("\n") # Trailing new line in file (or stdout)

        if len(args) == 1:
            os.rename(args[0] +  ".tmp", output_file)
