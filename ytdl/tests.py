import sys
import unittest
from django.test import TestCase


IS_PY2 = sys.version_info[0] == 2


class YoutubeTest(TestCase):
    def setUp(self):
        from ytdl.youtube_api import YoutubeApi
        self.api = YoutubeApi("roosterteeth")

    @unittest.skipIf(not IS_PY2, "need to rewrite YoutubeApi for Python 3")
    def test_list_videos(self):
        videos = list(self.api.videos_for_user(limit=1))

        assert len(videos) > 0
        for v in videos:
            assert 'url' in v
            assert 'title' in v
            assert 'id' in v
            assert 'youtube.com' in v['url']

    def test_icon(self):
        url = self.api.icon()
        assert url.startswith("http://") or url.startswith("https://")

        # .jpg seems only option, but might as well randomly guess at other options
        assert url.endswith(".jpg") or url.endswith(".png") or url.endswith(".gif")

    def test_title(self):
        title = self.api.title()
        assert title == "Rooster Teeth"


class VimeoTest(TestCase):
    def setUp(self):
        from ytdl.vimeo_api import VimeoApi
        self.api = VimeoApi("dbr")

    def test_list_videos(self):
        videos = list(self.api.videos_for_user(limit=1))

        assert len(videos) > 0
        for v in videos:
            assert 'url' in v
            assert 'title' in v
            assert 'id' in v
            assert 'vimeo.com' in v['url'], v['url']

    def test_icon(self):
        url = self.api.icon()
        assert url.startswith("http://") or url.startswith("https://")

        # .jpg seems only option, but might as well randomly guess at other options
        assert url.endswith(".jpg") or url.endswith(".png") or url.endswith(".gif")

    def test_title(self):
        title = self.api.title()
        assert title == "dbr", title


class ChannelRefresh(TestCase):

    @unittest.skipIf(not IS_PY2, "need to rewrite YoutubeApi for Python 3")
    def test_youtube_refresh(self):

        import ytdl.models

        chan = ytdl.models.Channel(chanid = 'roosterteeth', service=ytdl.models.YOUTUBE)
        chan.save()

        # Check title is updated
        chan.refresh_meta()
        assert chan.title == "Rooster Teeth" # TODO: Maybe assert != roosterteeth, since it could change?

        # Videos
        chan.grab(limit=1)
        videos = ytdl.models.Video.objects.all().filter(channel = chan)
        assert videos.count() > 0

    def test_vimeo_refresh(self):
        import ytdl.models

        chan = ytdl.models.Channel(chanid = 'dbr', service=ytdl.models.VIMEO)
        chan.save()

        # Check title is updated
        chan.refresh_meta()
        assert chan.title == "dbr"

        # Videos
        chan.grab(limit=1)
        videos = ytdl.models.Video.objects.all().filter(channel = chan)
        assert videos.count() > 0
