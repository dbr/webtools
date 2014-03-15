import requests
import xml.etree.ElementTree as ET


class YoutubeApi(object):
    def __init__(self, chanid):
        self.chanid = chanid

    def videos_for_user(self, limit=10):
        results = 50

        for offset_i in range(limit):
            offset = 1 + offset_i*results
            new = self._videos_for_user(offset=offset, results=results)

            for cur in new:
                yield cur

            if len(new) < results:
                raise StopIteration("No more videos on next page")

        else:
            print("Giving up at offset %s" % offset_i)

    def _videos_for_user(self, offset, results=50):
        import gdata.youtube.service
        yt_service = gdata.youtube.service.YouTubeService()
        uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?start-index=%d&max-results=%d' % (
            self.chanid,
            offset,
            results)

        feed = yt_service.GetYouTubeVideoFeed(uri)

        ret = []
        for item in feed.entry:
            id = item.id.text
            title = item.media.title.text
            url = item.media.player.url
            descr = item.media.description.text
            thumbs = [thumbnail.url for thumbnail in item.media.thumbnail]
            published = item.published.text
            import dateutil.parser
            dt = dateutil.parser.parse(published)

            info = {
                'id': id,
                'title': title or "Untitled",
                'url': url,
                'thumbs': thumbs,
                'descr': descr,
                'published': dt,
                }
            ret.append(info)

        if len(ret) < results:
            print("No more!")
        return ret

    def icon(self):
        url = 'http://gdata.youtube.com/feeds/api/users/%s?fields=yt:username,media:thumbnail' % (self.chanid)

        data = requests.get(url).text
        t = ET.fromstring(data)

        thumb = t.find("{http://search.yahoo.com/mrss/}thumbnail")
        return thumb.attrib['url']

    def title(self):
        uri = 'http://gdata.youtube.com/feeds/api/users/%s?fields=title' % (
            self.chanid)

        data = requests.get(uri).text
        t = ET.fromstring(data)

        elem = t.find("{http://www.w3.org/2005/Atom}title")
        return elem.text
