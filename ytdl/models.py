import datetime
import dateutil.tz

import peewee as p

from .youtube_api import YoutubeApi
from .vimeo_api import VimeoApi
from .settings import DB_PATH

database = p.SqliteDatabase(DB_PATH)


YOUTUBE = 'youtube'
VIMEO = 'vimeo'

ALL_SERVICES = [YOUTUBE, VIMEO]


def getnow():
    return datetime.datetime.now(dateutil.tz.tzlocal())


class BaseModel(p.Model):
    class Meta:
        database = database


class Channel(BaseModel):
    chanid = p.CharField(max_length=256)
    icon_url = p.CharField(max_length=1024, null=True)
    last_refresh = p.DateTimeField(null=True)
    last_update_content = p.DateTimeField(null=True)
    last_update_meta = p.DateTimeField(null=True)
    service = p.CharField(max_length=256, null=True)
    title = p.CharField(max_length=512, null=True)

    class Meta:
        db_table = 'ytdl_channel'

    def __unicode__(self):
        return "%s (%s on %s)" % (self.title, self.chanid, self.service)

    def get_api(self):
        if self.service == YOUTUBE:
            api = YoutubeApi(str(self.chanid))
        elif self.service == VIMEO:
            api = VimeoApi(str(self.chanid))
        else:
            raise ValueError("Unknown service %r" % self.service)

        return api

    def refresh_meta(self):
        """Get stuff like the channel title
        """
        api = self.get_api()
        now = getnow()

        new_title = api.title
        if self.title != new_title:
            self.title = self.get_api().title()
            self.last_update_meta = now
            self.save()

        new_icon = api.icon()
        if self.icon_url != new_icon:
            self.icon_url = new_icon
            self.last_update_meta = now
            self.save()

    def grab(chan, limit=1000, stop_on_existing=True):
        chan.last_refresh = getnow()
        chan.save()

        api = chan.get_api()

        with database.transaction():
            for vid in api.videos_for_user(limit=limit):
                exists = Video.select().where(Video.videoid == vid['id']).count() > 0
                if exists:
                    if stop_on_existing:
                        print("%s exists, stopping" % (vid['id']))
                        return
                    else:
                        print("%s exists. Onwards!" % (vid['id']))
                else:
                    # Save it
                    v = Video(
                        title = vid['title'],
                        url = vid['url'],
                        videoid = vid['id'],
                        description = vid['descr'],
                        channel = chan,
                        _thumbnails = "  ".join(vid['thumbs']),
                        publishdate = vid['published'],
                        )

                    # TODO: Less queries?
                    v.save()
                    chan.last_update_content = datetime.datetime.now(dateutil.tz.tzlocal())
                    chan.save()


class Video(BaseModel):
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


    _thumbnails = p.CharField(max_length=1024)
    channel = p.ForeignKeyField(Channel, related_name="videos")
    description = p.TextField(null=True)
    publishdate = p.DateTimeField()
    status = p.CharField(max_length=2, default=STATE_NEW)
    title = p.CharField(max_length=1024)
    url = p.CharField(max_length=1024)
    videoid = p.CharField(max_length=256)

    class Meta:
        db_table = 'ytdl_video'

    def __unicode__(self):
        return "%s (on %s) [%s]" % (self.title, self.channel.chanid, self.status)

    @property
    def img(self):
        return self._thumbnails.split("  ")
