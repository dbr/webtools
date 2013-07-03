from ytdl.models import Video, Channel
import ytdl.tasks

from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    from django.db.models import Count
    channels = Channel.objects.all().annotate(num_videos = Count('video'))
    recent = Video.objects.all().order_by('publishdate').reverse().filter(status=Video.STATE_NEW)[:5]

    # Show "active" videos (downloading, errored, queued)
    downloads = Video.objects.filter(Q(status=Video.STATE_DOWNLOADING) | Q(status=Video.STATE_QUEUED) | Q(status=Video.STATE_GRAB_ERROR)).reverse().all()

    return render_to_response(
        'ytdl/list_channels.html',
        {"channels": channels, "recent": recent, "downloads": downloads})


def view_channel(request, channame):
    all_videos = Video.objects.order_by('publishdate').reverse().all()
    if channame == "_all":
        channel = None
    else:
        channel = get_object_or_404(Channel, chanid=channame)
        all_videos = all_videos.filter(channel=channel)

    query = request.GET.get('search', "")
    if len(query) > 0:
        all_videos = all_videos.filter(title__icontains=query)

    # Filtering by status
    # FIXME: Expose/retain this in webUI
    status = request.GET.get('status', "")
    if len(status) > 0:
        all_videos = all_videos.filter(status=status)

    # 25 videos per page, with no less than 5 per page
    paginator = Paginator(all_videos, per_page=25, orphans=5)


    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    return render_to_response('ytdl/view_channel.html',
                              {"channel": channel,
                               "videos": videos,
                               "query": query})


def grab(request, videoid):
    video = get_object_or_404(Video, id=videoid)

    force = request.REQUEST.get("force", "false").lower() == "true"

    grabbable = video.status in [Video.STATE_NEW, Video.STATE_GRAB_ERROR]
    if not grabbable and not force:
        return HttpResponse(
            "Bad. Already grabbed (status %s)" % (video.status),
            status=500)

    video.status = Video.STATE_QUEUED
    video.save()
    ytdl.tasks.grab_video.delay(video.id, force=force)
    return HttpResponse("ok" + " (force)"*(int(force)))


def mark_viewed(request, videoid):
    video = get_object_or_404(Video, id=videoid)
    video.status = Video.STATE_GRABBED
    video.save()

    return HttpResponse("ok")


def refresh_all(request):
    channels = Channel.objects.all()
    for c in channels:
        ytdl.tasks.refresh_channel.delay(id=c.id)

    return HttpResponse("ok")


def refresh_channel(request, chanid):
    channel = get_object_or_404(Channel, id=chanid)
    ytdl.tasks.refresh_channel.delay(id=channel.id)

    return HttpResponse("ok")


def add_channel(request, channame):
    # Ensure channel doesn't exist yet
    try:
        Channel.objects.get(chanid=channame)
    except Channel.DoesNotExist:
        pass
    else:
        return HttpResponse("exists", status=500)

    # Create new channel
    channel = Channel(chanid=channame)
    channel.save()

    # Trigger refresh
    ytdl.tasks.refresh_channel.delay(id=channel.id)
    return HttpResponse("ok")
