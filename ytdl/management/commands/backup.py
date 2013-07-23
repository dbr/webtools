import os
import sys
import json

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Write out channel list"

    def handle(self, *args, **kwargs):
        if len(args) == 1:
            output_file = args[0]
            f = open(output_file +  ".tmp", "w+")
        elif len(args) == 0:
            f = sys.stdout
        else:
            raise CommandError("First argument is output file. If unspecified, writes to stdout")


        videos = {}

        import ytdl.models
        all_chan = ytdl.models.Channel.objects.all()
        for c in all_chan:
            channel_videos = ytdl.models.Video.objects.filter(channel = c)
            for v in channel_videos:
                videos.setdefault(c.chanid, []).append(
                    {'title': v.title,
                     'url': v.url,
                     'status': v.status,
                     'publishdate': v.status,
                 })

        json.dump(videos, f,
                         sort_keys=True,
                         indent=1, separators=(',', ': '))
        f.write("\n") # Trailing new line in file (or stdout)

        if len(args) == 1:
            os.rename(args[0] +  ".tmp", output_file)
