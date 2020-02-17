import sys
from unittest import TestCase
from mypy_extensions import NoReturn


IS_PY2 = sys.version_info[0] == 2

import peewee


class YoutubeTest(TestCase):
    def setUp(self):
        # type: () -> None
        super(YoutubeTest, self).setUp()
        from ytdl.youtube_api import YoutubeApi
        self.api = YoutubeApi("roosterteeth")

    def test_list_videos(self):
        # type: () -> None
        videos = list(self.api.videos_for_user(limit=1))

        assert len(videos) > 0
        for v in videos:
            assert 'url' in v
            assert 'title' in v
            assert 'id' in v
            assert 'youtube.com' in v['url']

    def test_icon(self):
        # type: () -> None
        url = self.api.icon()
        assert url.startswith("http://") or url.startswith("https://")

    def test_title(self):
        # type: () -> None
        title = self.api.title()
        assert title == "Rooster Teeth"


class VimeoTest(TestCase):
    def setUp(self):
        # type: () -> None
        super(VimeoTest, self).setUp()
        from ytdl.vimeo_api import VimeoApi
        self.api = VimeoApi("dbr")

    def test_list_videos(self):
        # type: () -> None
        videos = list(self.api.videos_for_user(limit=1))

        assert len(videos) > 0
        for v in videos:
            assert 'url' in v
            assert 'title' in v
            assert 'id' in v
            assert 'vimeo.com' in v['url'], v['url']

    def test_icon(self):
        # type: () -> None
        url = self.api.icon()
        assert url.startswith("http://") or url.startswith("https://")
        # Vimeo icons don't have file extension

    def test_title(self):
        # type: () -> None
        title = self.api.title()
        assert title == "dbr", title


class ChannelRefresh(TestCase):

    def test_youtube_refresh(self):
        # type: () -> None
        import ytdl.models

        chan = ytdl.models.Channel(chanid = 'roosterteeth', service=ytdl.models.YOUTUBE)
        chan.save()

        # Check title is updated
        chan.refresh_meta()
        assert chan.title == "Rooster Teeth" # TODO: Maybe assert != roosterteeth, since it could change?

        # Videos
        chan.grab(limit=1)
        videos = ytdl.models.Video.select().where(ytdl.models.Video.channel == chan)
        assert videos.count() > 0

    def test_vimeo_refresh(self):
        # type: () -> None
        import ytdl.models

        chan = ytdl.models.Channel(chanid = 'dbr', service=ytdl.models.VIMEO)
        chan.save()

        # Check title is updated
        chan.refresh_meta()
        assert chan.title == "dbr"

        # Videos
        chan.grab(limit=1)
        videos = ytdl.models.Video.select().where(ytdl.models.Video.channel == chan)
        assert videos.count() > 0
