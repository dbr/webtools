from django.db import models

import datetime
import django.utils.timezone
from django.core.cache import cache

from .youtube_api import YoutubeApi
from .vimeo_api import VimeoApi



YOUTUBE = 'youtube'
VIMEO = 'vimeo'

ALL_SERVICES = [YOUTUBE, VIMEO]


class Channel(models.Model):
    chanid = models.CharField(max_length=256, unique=True)
    service = models.CharField(max_length=256, unique=True)

    def __unicode__(self):
        return self.chanid

    def get_api(self):
        if self.service == YOUTUBE:
            api = YoutubeApi(str(self.chanid))
        elif self.service == VIMEO:
            api = VimeoApi(str(self.chanid))
        else:
            raise ValueError("Unknown service %r" % self.service)

        return api

    def grab(self, limit=1000):
        chan = self.get_api()

        for vid in chan.videos_for_user(limit=limit):
            exists = Video.objects.filter(videoid = vid['id']).count() > 0
            if exists:
                print "%s exists, stopping" % (vid['id'])
                return # Skip

            from pprint import pprint as pp
            pp(vid)
            v = Video(
                title = vid['title'],
                url = vid['url'],
                videoid = vid['id'],
                description = vid['descr'],
                channel = self,
                _thumbnails = "  ".join(vid['thumbs']),
                publishdate = vid['published'],
                )

            # TODO: Bulk insertion, https://docs.djangoproject.com/en/dev/topics/db/optimization/#insert-in-bulk
            v.save()

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('ytdl.views.view_channel', args=[self.id, ])

    def num_unviewed_recently(self, _clear_cache=False):
        key = "video__num_unviewed_recently__%s" % self.id

        if _clear_cache:
            cache.delete(key)
            return

        cached_val = cache.get(key)
        if cached_val is not None:
            return cached_val

        now = django.utils.timezone.now()
        range = datetime.timedelta(days=7)
        newer_than = now - range
        val = Video.objects.filter(channel=self).filter(status=Video.STATE_NEW).filter(publishdate__gt=newer_than).count()
        cache.set(key, val)
        return val

    def num_unviewed(self, _clear_cache=False):
        key = "video__num_unviewed__%s" % self.id

        if _clear_cache:
            cache.delete(key)
            return

        cached_val = cache.get(key)
        if cached_val is not None:
            return cached_val

        val = Video.objects.filter(channel=self).filter(status=Video.STATE_NEW).count()
        cache.set(key, val)
        return val

    def video_updated(self):
        # When video is updated, invalidate cached things like num_unviewed count
        self.num_unviewed(_clear_cache=True)
        self.num_unviewed_recently(_clear_cache=True)


class Video(models.Model):
    STATE_NEW = 'NE'
    STATE_QUEUED = 'QU'
    STATE_DOWNLOADING = 'DL'
    STATE_GRABBED = 'GR'
    STATE_GRAB_ERROR = 'GE'
    STATE_IGNORE = 'IG'

    STATES = (
        (STATE_NEW, 'New video'),
        (STATE_QUEUED, 'Queued for download, but not begun yet'),
        (STATE_DOWNLOADING, 'Downloading'),
        (STATE_GRABBED, 'Grabbing video now'),
        (STATE_GRAB_ERROR, 'Error while grabbing video'),
        (STATE_IGNORE, 'Ignored video'),
        )

    channel = models.ForeignKey(Channel)                  # Channel to which this belongs
    url = models.CharField(max_length=1024)               # Youtube URL
    title = models.CharField(max_length=1024)             # Title of video
    description = models.TextField(blank=True, null=True) # Description of video
    _thumbnails = models.CharField(max_length=1024)       # Thumbnail image URL
    videoid = models.CharField(max_length=256)            # ID of video on service
    publishdate = models.DateTimeField(db_index=True)     # When the video was originally published
    status = models.CharField(max_length=2, choices=STATES, default=STATE_NEW, db_index=True)

    # Index on publishdate helps with pagination query (SELECT * FROM ytdl_video ORDER BY publishdate)

    # Index on status helps "Downloads" query (SELECT * FROM ytdl_video WHERE status=DL or status=QU etc)

    # Multi-column index, only works in Django 1.5+
    index_together = [
        # For "num_unviewed_recently"
        ["status", "publishdate"],
    ]

    def __unicode__(self):
        return "%s (on %s) [%s]" % (self.title, self.channel.chanid, self.status)

    @property
    def status_class(self):
        #FIXME: Doesn't even remotely belong here
        classmap = {
            self.STATE_NEW: 'info',
            self.STATE_QUEUED: 'pending',
            self.STATE_DOWNLOADING: 'pending',
            self.STATE_GRABBED: 'success',
            self.STATE_GRAB_ERROR: 'error',
            self.STATE_IGNORE: '',
            }

        return classmap.get(self.status, "error")

    @property
    def status_str(self):
        #FIXME: Doesn't even remotely belong here
        classmap = {
            self.STATE_NEW: 'New',
            self.STATE_QUEUED: 'Queued',
            self.STATE_DOWNLOADING: 'Downloading',
            self.STATE_GRABBED: 'Grabbed',
            self.STATE_GRAB_ERROR: 'Grab error',
            self.STATE_IGNORE: 'Ignored',
            }

        return classmap.get(self.status, "error")

    @property
    def img(self):
        return self._thumbnails.split("  ")

    def save(self, *args, **kwargs):
        # Invalidate cached stuff on channel (e.g video totals)
        self.channel.video_updated()

        super(Video, self).save(*args, **kwargs)
