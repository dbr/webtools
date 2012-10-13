import os
import subprocess
from celery import task


from ytdl.models import Video, Channel


@task
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
    print "Starting to grab %s" % video
    video.status = Video.STATE_DOWNLOADING
    video.save()

    cwd = os.path.expanduser("~/Downloads")
    p = subprocess.Popen(
        ["youtube-dl", "--title", video.url],
        cwd = cwd)

    p.communicate()

    video.status = Video.STATE_GRABBED
    video.save()
    print "Done: %s" % video


@task
def refresh_channel(id):
    channel = Channel.objects.get(id=id)
    channel.grab()
