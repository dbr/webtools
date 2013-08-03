import os
import sys
import json

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "From a backup restores the list of channels, lists the videos from the service and restores the grabbed-status"

    def handle(self, *args, **kwargs):
        if len(args) == 1:
            output_file = args[0]
            f = open(output_file)
        elif len(args) == 0:
            f = sys.stdin.read()
        else:
            raise CommandError("First argument is output file. If unspecified, writes to stdout")

        import ytdl.models

        all_chan = json.load(f)
        for channel in all_chan:
            try:
                db_chan = ytdl.models.Channel.objects.get(chanid=channel['chanid'])
            except ytdl.models.Channel.DoesNotExist:
                print "Creating %s (service %s)" % (channel['chanid'], channel['service'])
                db_chan = ytdl.models.Channel(chanid = channel['chanid'], service=channel['service'])
                db_chan.save()

            # Get videos form channel
            print "Getting videos for %s" % (db_chan)
            db_chan.grab()

            print "Updating statuses"
            for video in channel['videos']:
                try:
                    v = ytdl.models.Video.objects.get(videoid=video['videoid'])
                except ytdl.models.Video.DoesNotExist:
                    print "%s does not exist (title: %s)" % (video['videoid'], video['title'])
                    continue # Next video
                v.status = video['status']
                v.save()
