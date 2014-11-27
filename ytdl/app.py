import json
from flask import Flask
from flask import abort, redirect, url_for, send_file
from ytdl.paginator import Paginator, PageNotAnInteger, EmptyPage

import ytdl.settings
import ytdl.tasks
from ytdl.models import Video, Channel

from rq_dashboard import RQDashboard


app = Flask(__name__)

# Setup rq dashboard
RQDashboard(app)


# Serving of single-page app
@app.route("/")
def index():
    return redirect("/youtube/", code=302)


@app.route("/youtube/")
def page():
    return send_file("static/ytdl.html")


@app.route("/youtube2/")
def page2():
    return send_file("static/ytdl2.html")




# API

def _channel_info_dict(c):
    return {
        'id': c.id,
        'title': c.title,
        'service': c.service,
        'id': c.id,
        'icon': c.icon_url,
        'last_refresh': str(c.last_refresh),
        'last_content_update': str(c.last_update_content),
        'last_meta_update': str(c.last_update_meta),
    }


@app.route("/youtube/api/1/refresh")
def refresh():
    chanid = request.args.get("channel")
    if chanid == "_all":
        ytdl.tasks.refresh_all_channels()
        return json.dumps({"message": "refreshing all channels"})
    else:
        chan = Channel.get(id=chanid)
        if chan is None:
            return json.dumps({"error": "so such channel"}), 404
        ytdl.tasks.refresh_channel.delay(id=chan.id)
        return json.dumps({"message": "refreshing channel %s (%s)" % (chan.id, chan.title)})

from flask import request
@app.route("/youtube/api/1/channels")
def list_channels():
    page = int(request.args.get("page", "1"))
    count = request.args.get("count")

    def offset(sliceable, page, count):
        start = (page - 1) * count
        end = page * count
        return sliceable[start:end]

    query = Channel.select().order_by('title')
    if count is not None:
        count = int(count)
        query = offset(query, page, count)

    channels = []
    for c in query:
        channels.append(_channel_info_dict(c))
    return json.dumps({'channels': channels, 'total': Channel.select().count()})


@app.route("/youtube/api/1/channels/<chanid>")
def channel_details(chanid):
    if chanid == "_all":
        query = Video.select()
    else:
        chan = Channel.get(id=chanid)
        query = Video.select().filter(channel = chan)

    query = query.order_by(Video.publishdate.desc())

    search = request.args.get('search', "")
    if len(search) > 0:
        query = query.where(Video.title.contains(search))

    # Query based on status
    status = request.args.get('status', "")
    if len(status) > 0:
        status = status.strip().split(",")
        x = Video.status == status[0]
        for st in status[1:]:
            x = x | (Video.status == st)
        query = query.where(x)

    # 25 videos per page, with no less than 5 per page
    paginator = Paginator(query, per_page=25, orphans=5)

    # Get page parameter
    page_num = request.args.get('page', '1')
    if int(page_num) < 1:
        page_num = 1

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    out_videos = []
    for v in page:
        out_videos.append({
            'id': v.id,
            'title': v.title,
            'imgs': v.img,
            'url': v.url,
            'description': v.description,
            'publishdate': str(v.publishdate),
            'status': v.status,
            # FIXME: Data duplication, only used for "all" channel view
            'channel': _channel_info_dict(v.channel),
        })

    if chanid == '_all':
        channel = None
    else:
        channel = _channel_info_dict(chan)

    page_info = {
        'total': paginator.num_pages,
        'current': page.number,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        }

    return json.dumps(
        {'channel': channel,
         'videos': out_videos,
         'pagination': page_info})



@app.route("/youtube/api/1/video/<videoid>/grab")
def grab(videoid):
    """For a given video ID, enqueue the task to download it
    """

    video = Video.get(id=videoid)
    if video is None:
        abort(404)

    force = request.args.get("force", "false").lower() == "true"

    grabbable = video.status in [Video.STATE_NEW, Video.STATE_GRAB_ERROR, Video.STATE_IGNORE]
    if not grabbable and not force:
        ret = {"error": "Already grabbed (status %s)" % (video.status)}
        return json.dumps(ret), 500

    ytdl.tasks.grab_video.delay(video.id, force=force)

    video.status = Video.STATE_QUEUED
    video.save()

    return json.dumps({"status": video.status})


# Set status

def _set_status(videoid, status):
    video = Video.get(id=videoid)
    if video is None:
        abort(404)

    video.status = status
    video.save()
    return json.dumps({"status": video.status})


@app.route('/youtube/api/1/video/<videoid>/mark_viewed')
def mark_viewed(videoid):
    return _set_status(videoid, Video.STATE_GRABBED)


@app.route('/youtube/api/1/video/<videoid>/mark_ignored')
def mark_ignored(videoid):
    return _set_status(videoid, status=Video.STATE_IGNORE)


# Query status

@app.route('/youtube/api/1/video_status')
def video_status():
    ids = request.args.get("ids")
    if ids is None:
        return "{}"

    ids = ids.split(",")
    videos = {}
    for cur in ids:
        v = Video.get(id=cur)
        if v is None:
            abort(404)
        videos[int(cur)] = v.status

    return json.dumps(videos)


@app.route("/youtube/api/1/downloads")
def list_downloads():
    query = Video.select().where(
        (Video.status==Video.STATE_DOWNLOADING)
        | (Video.status == Video.STATE_QUEUED)
        | (Video.status == Video.STATE_GRAB_ERROR)
    )

    downloads = []
    for dl in query:
        downloads.append({"id": dl.id,
                          "status": dl.status,
                          "title": dl.title})

    return json.dumps(
        {"downloads": downloads,
     })


@app.before_request
def before_request():
    ytdl.models.database.init(ytdl.settings.DB_PATH)


if __name__ == "__main__":
    app.debug=True
    app.run()
