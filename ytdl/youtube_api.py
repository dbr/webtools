import logging
import requests
from typing import Any, Dict, Iterator, Union, List, Optional, Tuple, Generator


log = logging.getLogger(__name__)


class YoutubeApi(object):
    API_KEY = "AIzaSyBBUxzImakMKKW3B6Qu47lR9xMpb6DNqQE" # ytdl public API browser key (for Youtube API v3)

    def __init__(self, chanid):
        # type: (str) -> None
        self.chanid = chanid

    def videos_for_user(self, limit=10):
        # type: (int) -> Generator[Dict[str, Any], None, None]
        url = "https://www.googleapis.com/youtube/v3/channels?key={apikey}&forUsername={chanid}&part=contentDetails".format(
            apikey = self.API_KEY,
            chanid = self.chanid)
        resp = requests.get(url)
        if len(resp.json()['items']) == 0:
            log.warning("No items found at %s - trying as ID" % url)

            # FIXME: Store consistent data - either channel ID or username
            url = "https://www.googleapis.com/youtube/v3/channels?key={apikey}&id={chanid}&part=contentDetails".format(
                apikey = self.API_KEY,
                chanid = self.chanid)
            resp = requests.get(url)
            if len(resp.json()['items']) == 0:
                log.warning("No items found at %s either" % url)

        upload_playlist = resp.json()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        next_page = None
        for x in range(limit):
            cur, next_page = self._videos_for_playlist(playlist_id=upload_playlist, page_token=next_page)
            for c in cur:
                yield c
            if next_page is None:
                break # Signifies no more pages

    def _videos_for_playlist(self, playlist_id, page_token=None):
        # type: (str, Optional[Any]) -> Tuple[List[Dict[str, Any]], str]
        if page_token is None:
            pt = ""
        else:
            pt = "&pageToken={p}".format(p=page_token)

        url = "https://www.googleapis.com/youtube/v3/playlistItems?key={apikey}&part=snippet&maxResults={num}&playlistId={playlist}{page}".format(
            apikey = self.API_KEY,
            num=50,
            playlist = playlist_id,
            page=pt
        )

        resp = requests.get(url)
        data = resp.json()

        ret = []
        for v in data['items']:
            s = v['snippet']

            import dateutil.parser
            dt = dateutil.parser.parse(s['publishedAt'])

            thumbs = [s['thumbnails']['default']['url'], ]

            info = {
                'id': "http://gdata.youtube.com/feeds/api/videos/%s" % s['resourceId']['videoId'], # TODO: Migrate form silly gdata ID in database
                'title': s['title'],
                'url': 'http://youtube.com/watch?v={id}'.format(id=s['resourceId']['videoId']),
                'thumbs': thumbs,
                'descr': s['description'],
                'published': dt,
                }

            ret.append(info)

        return ret, data.get('nextPageToken')

    def _chan_snippet(self):
        # type: () -> Optional[Dict[str, Any]]
        url = "https://www.googleapis.com/youtube/v3/channels?key={apikey}&forUsername={chanid}&part=snippet".format(
            apikey = self.API_KEY,
            chanid = self.chanid,
            )

        items = requests.get(url).json()['items']
        if len(items) > 0:
            return items[0]['snippet']
        else:
            log.warning("No items found at %s - trying as ID" % (url))
            url = "https://www.googleapis.com/youtube/v3/channels?key={apikey}&id={chanid}&part=snippet".format(
                apikey = self.API_KEY,
                chanid = self.chanid,
                )
            items = requests.get(url).json()['items']
            if len(items) > 0:
                return items[0]['snippet']
            else:
                log.warning("No items found at %s either" % (url))
                return None


    def icon(self):
        # type: () -> str
        snippet = self._chan_snippet()
        if snippet is None:
            return "" # FIXME?
        return snippet['thumbnails']['default']['url']

    def title(self):
        # type: () -> str
        snippet = self._chan_snippet()
        if snippet is None:
            return "(no title)"
        return snippet['title']


if __name__ == '__main__':
    y = YoutubeApi("roosterteeth")
    print(y.icon())
    print(y.title())
    for v in y.videos_for_user():
        print(v['title'])
