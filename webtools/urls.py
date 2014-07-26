import ytdl.urls
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webtools.views.home', name='home'),
    # url(r'^webtools/', include('webtools.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^django-rq/', include('django_rq.urls')),

    url(r'^$', RedirectView.as_view(url='youtube/')),
    url(r'^youtube/', include(ytdl.urls)),
)


from django.conf import settings

if not settings.DEBUG:
    # http://stackoverflow.com/questions/9047054/heroku-handling-static-files-in-django-app
    urlpatterns += patterns(
        '',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        )
