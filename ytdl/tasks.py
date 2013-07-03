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

    cwd = os.path.expanduser("~/Movies/ytdl")

    try:
        os.makedirs(cwd)
    except OSError, e:
        if e.errno == 17:
            # Ignore errno 17 (File exists)
            pass
        else:
            raise

    # Get output filename
    output_format = "%(upload_date)s_%(stitle)s%(ext)s_%(id)s"
    p = subprocess.Popen(
        ["youtube-dl", "--output", output_format, video.url, "--get-filename"],
        cwd = cwd,
        stdout = subprocess.PIPE)
    so, _se = p.communicate()

    if p.returncode != 0:
        video.status = Video.STATE_GRAB_ERROR
        video.save()
        print "Error grabbing video %s" % video
        return

    # FIXME: Store this in DB
    filename = os.path.join(cwd, so.strip())

    p = subprocess.Popen(
        ["youtube-dl", "--output", "%(upload_date)s_%(stitle)s_%(id)s.%(ext)s", video.url],
        cwd = cwd)

    p.communicate()

    if p.returncode != 0:
        video.status = Video.STATE_GRAB_ERROR
        video.save()
        print "Error grabbing %s" % video
        return

    else:
        video.status = Video.STATE_GRABBED
        video.save()
        print "Done: %s" % video


@task
def refresh_channel(id):
    channel = Channel.objects.get(id=id)
    channel.grab()
