import logging
import requests
import xmltodict


log = logging.getLogger(__name__)


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
            log.debug("Giving up at offset %s" % offset_i)

    def _videos_for_user(self, offset, results=50):
        uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?start-inde=%d&max-results=%d' % (
            self.chanid,
            offset,
            results)
        data = requests.get(uri).text

        t = xmltodict.parse(data)

        ret = []
        for item in t['feed']['entry']:
            id = item['id']
            title = item['media:group']['media:title']['#text']
            url = item['media:group']['media:player']['@url']
            descr = item['media:group']['media:description'].get('#text')
            thumbs = [thumbnail['@url'] for thumbnail in item['media:group']['media:thumbnail']]
            published = item['published']
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

        return ret

    def icon(self):
        url = 'http://gdata.youtube.com/feeds/api/users/%s?fields=yt:username,media:thumbnail' % (self.chanid)

        data = requests.get(url).text
        t = xmltodict.parse(data)
        return t['entry']['media:thumbnail']['@url']

    def title(self):
        uri = 'http://gdata.youtube.com/feeds/api/users/%s?fields=title' % (
            self.chanid)

        data = requests.get(uri).text
        t = xmltodict.parse(data)

        return t['entry']['title'].get('#text')
