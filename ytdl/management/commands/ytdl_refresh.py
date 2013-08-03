from django.core.management.base import BaseCommand, CommandError

from ytdl.tasks import refresh_channel


class Command(BaseCommand):
    help = "Check for new videos"

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError("Expected one argument of the channel name, got %s: %r" % (
                    len(args),
                    args))

        import ytdl.models
        try:
            chan = ytdl.models.Channel.objects.get(chanid=args[0])
        except ytdl.models.Channel.DoesNotExist:
            print "New channel %s" % args[0]
            chan = ytdl.models.Channel(chanid=args[0])
            chan.save()

        refresh_channel.delay(chan.id)
