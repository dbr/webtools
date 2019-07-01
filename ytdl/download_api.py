import logging
import traceback

import redis
import youtube_dl
import ytdl.settings


HOUR = 60*60 # 60 seconds in minute, 60 minutes in hour


log = logging.getLogger(__name__)



class YDL(object):
    def __init__(self, id, url, outtmpl):
        self.id = id
        self.url = url
        self.r = redis.Redis(host=ytdl.settings.REDIS_HOST, port=ytdl.settings.REDIS_PORT)
        self.outtmpl = outtmpl

    def debug(self, msg):
        log.debug("YTDL DEBUG: %s" % msg)
        self._append_log("[debug] %s" % msg)

    def warning(self, msg):
        log.debug("YTDL WARNING: %s" % msg)
        self._append_log("[warning] %s" % msg)

    def error(self, msg):
        log.debug("YTDL ERROR: %s" % msg)
        self._append_log("[error] %s" % msg)

    def _set_progress(self, percent=None, status=None, msg=None):
        key = "dl:{id}:info".format(id=self.id)
        if status:
            self.r.hset(key, "status", status)
            self.r.expire(key, 1*HOUR)
        if percent:
            self.r.hset(key, "progress", percent)
            self.r.expire(key, 1*HOUR)
        if msg:
            self.r.hset(key, "message", msg)
            self.r.expire(key, 1*HOUR)

    def _append_log(self, line):
        key = "dl:{id}:log".format(id=self.id)
        self.r.rpush(key, line)
        self.r.ltrim(key, -100, -1) # Keep only last 100 lines
        self.r.expire(key, 1*HOUR)

    def progress_hook(self, d):
        def human(byt):
            return "%.02fMiB" % (byt/1024.0/1024.0)
        def human_seconds(sec):
            return "%02d:%02d" % (sec//60, sec%60)
        if d['status'] == 'downloading':
            downloaded = float(d.get("downloaded_bytes", 0))
            total = float(d.get("total_bytes", 1))
            percent = 100*(float(downloaded) / float(total))
            msg = "%3.01f%% of %s at %.02fKiB/s ETA %s" % (
                percent,
                human(total),
                (d.get('speed') or 0)/1024.0,
                human_seconds(d.get('eta') or 0))

            self._set_progress(status=d['status'], percent=percent, msg=msg)

        elif d['status'] == 'finished':
            self._set_progress(status=d['status'])
            self._append_log("done")

            # Remove from active-download set
            self.r.srem("dl", self.id)

    def go(self):
        opts = {}
        opts['logger'] = self
        opts['progress_hooks'] = [self.progress_hook]

        opts['restrictfilenames'] = True
        opts['continuedl'] = True
        opts['outtmpl'] = self.outtmpl

        # Add to active-download set
        self.r.sadd("dl", self.id)

        # Clean up stale data
        self.r.delete("dl:{id}:info".format(id=self.id))
        self.r.delete("dl:{id}:log".format(id=self.id))

        self._set_progress(status="new")

        with youtube_dl.YoutubeDL(opts) as ydl:
            log.info("Beginning downloading %s" % (self.url))
            try:
                ydl.download([self.url])
            except youtube_dl.DownloadError as e:
                self._set_progress(status="error", msg='%s' % e)
                for line in traceback.format_exc():
                    self._append_log(line=line)
                raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    import random
    d = YDL(id=random.randint(1, 100),
            url='http://www.youtube.com/watch?v=BaW_jenozKc')
    d.go()
