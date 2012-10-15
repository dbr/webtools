from django.conf.urls import patterns, url


urlpatterns = patterns(
    'ytdl.views',

    url(r'^$', 'index'),
    url(r'^channel/(?P<channame>.+)', 'view_channel'),
    url(r'^channel_add/(?P<channame>.+)', 'add_channel'),

    url(r'^grab/(?P<videoid>\d+)', 'grab'),
    url(r'^viewed/(?P<videoid>\d+)', 'mark_viewed'),
    url(r'^refresh/(?P<chanid>\d+)', 'refresh_channel'),
)

