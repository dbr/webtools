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
    for c in Channel.objects.all():
        channels.append({
            'id': c.id,
            'title': c.title,
            'service': c.service,
        })
    return HttpResponse(json.dumps({'channels': channels}))


def channel_details(request, chanid):
    chan = Channel.objects.get(id=chanid)

    videos = []
    for v in Video.objects.all().filter(channel = chan)[:10]:
        videos.append({
            'id': v.id,
            'title': v.title,
        })
    return HttpResponse(json.dumps({'videos': videos}))
