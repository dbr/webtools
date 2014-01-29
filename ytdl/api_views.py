import json

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ytdl.models import Video, Channel, ALL_SERVICES


def test(request):
    return render_to_response("ytdl/api_test.html")


def list_channels(request):
    channels = []
    for c in Channel.objects.order_by('title').all():
        channels.append({
            'id': c.id,
            'title': c.title,
            'service': c.service,
        })
    return HttpResponse(json.dumps({'channels': channels}))


def channel_details(request, chanid):
    if chanid == "all":
        query = Video.objects.all()
    else:
        chan = Channel.objects.get(id=chanid)
        query = Video.objects.all().filter(channel = chan)
    query = query.order_by('publishdate').reverse()[:25]

    videos = []
    for v in query:
        videos.append({
            'id': v.id,
            'title': v.title,
            'imgs': v.img,
            'description': v.description,
            'publishdate': str(v.publishdate),
            'status': v.status,
            'channel': {
                'title': v.channel.title,
                'chanid': v.channel.chanid,
                'service': v.channel.service,
                },
        })

    if chanid == 'all':
        channel = None
    else:
        channel = {
            'title': v.channel.title,
            'chanid': v.channel.chanid,
            'service': v.channel.service,
            }

    return HttpResponse(json.dumps({'channel': channel, 'videos': videos}))
