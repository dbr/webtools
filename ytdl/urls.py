from django.conf.urls import patterns, url


urlpatterns = patterns(
    'ytdl.views',

    url(r'^$', 'index'),
    url(r'^channel/(?P<chanid>.+)', 'view_channel'),
    url(r'^channel_add', 'add_channel'),
    url(r'^channel_add/(?P<channame>.+)', 'add_channel'),
    url(r'^channel_delete', 'channel_delete'),

    url(r'^grab/(?P<videoid>\d+)', 'grab'),
    url(r'^viewed/(?P<videoid>\d+)', 'mark_viewed'),
    url(r'^ignored/(?P<videoid>\d+)', 'mark_ignored'),
    url(r'^refresh/(?P<chanid>\d+)', 'refresh_channel'),
    url(r'^refresh_all', 'refresh_all'),
)

urlpatterns += patterns(
    'ytdl.api_views',

    url(r'^api/1/test', 'test'),
    url(r'^api/1/channels$', 'list_channels'),
    url(r'^api/1/channels/(?P<chanid>\d+|all)$', 'channel_details'),

    url(r'^api/1/video/(?P<videoid>\d+)/grab$', 'grab'),
    url(r'^api/1/video/(?P<videoid>\d+)/mark_viewed$', 'mark_viewed'),
    url(r'^api/1/video/(?P<videoid>\d+)/mark_ignored$', 'mark_ignored'),

    url(r'^api/1/video_status$', 'video_status'),
    url(r'^api/1/downloads$', 'list_downloads'),
)
