import os
import logging
import subprocess
from django_rq import job as task


from ytdl import ytdl_settings
from ytdl.models import Video, Channel


log = logging.getLogger(__name__)

QUEUE_DEFAULT = "ytdl-default"
QUEUE_DOWNLOAD = "ytdl-download"


@task(QUEUE_DOWNLOAD)
def grab_video(videoid, force=False):
    # Get video from DB
    video = Video.objects.get(id=videoid)

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

    cwd = ytdl_settings.OUTPUT_DIR

    try:
        os.makedirs(cwd)
    except OSError as e:
        if e.errno == 17:
            # Ignore errno 17 (File exists)
            pass
        else:
            raise

    # Get output filename
    p = subprocess.Popen(
        ["youtube-dl", "--restrict-filenames", "--output", ytdl_settings.OUTPUT_FORMAT, video.url, "--get-filename"],
        cwd = cwd,
        stdout = subprocess.PIPE)
    so, _se = p.communicate()

    if p.returncode != 0:
        video.status = Video.STATE_GRAB_ERROR
        video.save()
        log.error("Error grabbing video name %s - non-zero return code %s" % (video, p.returncode))
        return

    # FIXME: Store this in DB
    filename = os.path.join(cwd, so.strip())

    # Grab video
    cmd = ["youtube-dl", "--restrict-filenames", "--output", ytdl_settings.OUTPUT_FORMAT, video.url]
    cmd.extend(ytdl_settings.YOUTUBE_DL_FLAGS)
    p = subprocess.Popen(cmd, cwd = cwd)

    p.communicate()

    if p.returncode != 0:
        video.status = Video.STATE_GRAB_ERROR
        video.save()
        log.error("Error grabbing %s - non-zero return code %s" % (video, p.returncode))
        return

    else:
        video.status = Video.STATE_GRABBED
        video.save()
        log.info("Grab complete %s" % video)


@task(QUEUE_DEFAULT)
def refresh_channel(id):
    log.debug("Refreshing channel %s" % id)
    channel = Channel.objects.get(id=id)
    log.debug("Refreshing channel metadata for %s" % (channel))
    channel.refresh_meta()
    log.debug("Grabbing from channel %s" % (channel))
    channel.grab()
    log.debug("Refresh complete for %s" % (channel))


@task(QUEUE_DEFAULT)
def refresh_all_channels(async=True):
    log.debug("Refreshing all channels")
    channels = Channel.objects.all()
    for c in channels:
        if async:
            refresh_channel.delay(id=c.id)
        else:
            refresh_channel(id=c.id)
