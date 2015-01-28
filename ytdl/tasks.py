import os
import logging

from redis import Redis
from rq import Queue

import ytdl.settings
import ytdl.download_api


def get_queue(queue):
    redis_conn = Redis()
    q = Queue(queue, connection=redis_conn)
    return q


def task(queue_name, *queue_args, **queue_kwargs):
    def decorator_creation(func):
        def delay(*func_args, **func_kwargs):
            q = get_queue(queue_name)
            t = q.enqueue_call(func, args=func_args, kwargs=func_kwargs,
                               *queue_args, **queue_kwargs)
            return t
        func.delay = delay
        return func

    return decorator_creation


import ytdl.settings
from ytdl.models import Video, Channel


log = logging.getLogger(__name__)

QUEUE_DEFAULT = "ytdl-default"
QUEUE_DOWNLOAD = "ytdl-download"


HOUR = 60*60
@task(QUEUE_DOWNLOAD, timeout=2*HOUR)
def grab_video(videoid, force=False):
    # Get video from DB
    video = Video.get(id=videoid)

    # Validation
    grabbable = video.status in [Video.STATE_NEW, Video.STATE_GRAB_ERROR, Video.STATE_QUEUED]

    if not grabbable and not force:
        emsg = "%s status not NEW or GRAB_ERROR, and force was %s" % (
            video, force)
        raise ValueError(emsg)

    if force and video.status == Video.STATE_DOWNLOADING:
        raise ValueError("Already downloading")

    # Grab video
    log.info("Starting to grab %s" % video)
    video.status = Video.STATE_DOWNLOADING
    video.save()

    cwd = ytdl.settings.OUTPUT_DIR
    try:
        os.makedirs(cwd)
    except OSError as e:
        if e.errno == 17:
            # Ignore errno 17 (File exists)
            pass
        else:
            raise

    # Grab video
    outtmpl = os.path.join(ytdl.settings.OUTPUT_DIR, ytdl.settings.OUTPUT_FORMAT)
    x = ytdl.download_api.YDL(id=videoid, url=video.url, outtmpl=outtmpl)
    try:
        x.go()
    except Exception, e: # ?
        video.status = Video.STATE_GRAB_ERROR
        video.save()
        log.error("Error grabbing %s: %s" % (video, e), exc_info=True)
        return
    else:
        video.status = Video.STATE_GRABBED
        video.save()
        log.info("Grab complete %s" % video)


@task(QUEUE_DEFAULT)
def refresh_channel(id):
    log.debug("Refreshing channel %s" % id)
    channel = Channel.get(id=id)
    log.debug("Refreshing channel metadata for %s" % (channel))
    channel.refresh_meta()
    log.debug("Grabbing from channel %s" % (channel))
    channel.grab()
    log.debug("Refresh complete for %s" % (channel))


def refresh_all_channels(async=True):
    log.debug("Refreshing all channels")
    channels = Channel.select()
    for c in channels:
        if async:
            refresh_channel.delay(id=c.id)
        else:
            refresh_channel(id=c.id)
