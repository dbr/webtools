import sys
from unittest import TestCase
 
 
IS_PY2 = sys.version_info[0] == 2
 

class YtdlBaseTest(TestCase):
    def setUp(self):
        import ytdl.models
        ytdl.models.database.init(":memory:")

        import peewee
        import inspect
        models = [obj for name, obj in inspect.getmembers(ytdl.models)
                  if hasattr(obj, "__bases__") and ytdl.models.BaseModel in obj.__bases__]
        self.models = models
        peewee.create_model_tables(models)
    def tearDown(self):
        import peewee
        peewee.drop_model_tables(self.models)


class YoutubeTest(YtdlBaseTest):
    def setUp(self):
        super(YoutubeTest, self).setUp()
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
        super(VimeoTest, self).setUp()
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
 
 
class ChannelRefresh(YtdlBaseTest):
 
    def test_youtube_refresh(self):
 
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
