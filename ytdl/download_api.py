import redis
import youtube_dl

HOUR = 60*60 # 60 seconds in minute, 60 minutes in hour


class YDL(object):
    def __init__(self, id):
        self.id = id
        self.r = redis.Redis()

    def debug(self, msg):
        self._append_log("[debug] %s" % msg)

    def warning(self, msg):
        self._append_log("[warning] %s" % msg)

    def error(self, msg):
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
            percent = 100*(float(d['downloaded_bytes']) / float(d['total_bytes']))
            msg = "%3.01f%% of %s at %.02fKiB/s ETA %s" % (
                percent,
                human(d['total_bytes']),
                d.get('speed', 0)/1024.0,
                human_seconds(d.get('eta', 0)))

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

        # Add to active-download set
        self.r.sadd("dl", self.id)
        # Clean up stale data
        self.r.delete("dl:{id}:info".format(id=self.id))
        self.r.delete("dl:{id}:log".format(id=self.id))

        with youtube_dl.YoutubeDL(opts) as ydl:
            ydl.download(['http://www.youtube.com/watch?v=BaW_jenozKc'])


if __name__ == '__main__':
    d = YDL(id=1234)
    d.go()
