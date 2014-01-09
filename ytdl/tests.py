from django.test import TestCase


class YoutubeTest(TestCase):
    def setUp(self):
        from ytdl.youtube_api import YoutubeApi
        self.api = YoutubeApi("roosterteeth")

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
