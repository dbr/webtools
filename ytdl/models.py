from django.db import models

import gdata.youtube.service


class YoutubeApi(object):
    def __init__(self, chanid):
        self.chanid = chanid

    def videos_for_user(self, limit=10):
        results = 50

        print limit,"limit"
        for offset_i in range(limit):
            offset = 1 + offset_i*results
            print "offset", offset
            new = self._videos_for_user(offset=offset, results=results)

            for cur in new:
                yield cur

            if len(new) < results:
                raise StopIteration("No more videos on next page")

        else:
            print "Giving up at page %s" % offset_i

    def _videos_for_user(self, offset, results=50):
        yt_service = gdata.youtube.service.YouTubeService()
        uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?start-index=%d&max-results=%d' % (
            self.chanid,
            offset,
            results)

        print uri
        feed = yt_service.GetYouTubeVideoFeed(uri)
    
        ret = []
        for item in feed.entry:
            id = item.id.text
            title = item.media.title.text
            url = item.media.player.url
            descr = item.media.description.text
            thumbs = [thumbnail.url for thumbnail in item.media.thumbnail]
            published = item.published.text
            import time
            from datetime import datetime
            ts = time.strptime(published.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            dt = datetime.fromtimestamp(time.mktime(ts))
    
            info = {
                'id': id,
                'title': title or "Untitled",
                'url': url,
                'thumbs': thumbs,
                'descr': descr,
                'published': dt,
                }
            ret.append(info)

        if len(ret) < results:
            print "No more!\n\n\n\n"
        return ret


class Channel(models.Model):
    chanid = models.CharField(max_length=256, unique=True)

    def __unicode__(self):
        return self.chanid

    def grab(self, limit=10):
        chan = YoutubeApi(str(self.chanid))
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

            v.save()


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
    videoid = models.CharField(max_length=256)
    publishdate = models.DateTimeField()
    status = models.CharField(max_length=2, choices=STATES, default=STATE_NEW)

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
    def img(self):
        return self._thumbnails.split("  ")
