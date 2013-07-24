import datetime
import requests


class VimeoApi(object):
    def __init__(self, chanid):
        self.chanid = chanid

    def videos_for_user(self, limit=10):
        for page in range(3):
            page = page + 1
            url = "http://vimeo.com/api/v2/{chanid}/videos.json?page={page}".format(
                chanid = self.chanid,
                page = page)
            print url
            data = requests.get(url).json()
            for cur in data:
                dt = datetime.datetime.strptime(cur['upload_date'], "%Y-%m-%d %H:%M:%S")
                info = {
                    'id': cur['id'],
                    'title': cur['title'] or "Untitled",
                    'url': cur['url'],
                    'thumbs': [cur['thumbnail_medium'], ],
                    'descr': cur['description'],
                    'published': dt,
                }
                yield info

    def icon(self):
        data = requests.get("http://vimeo.com/api/v2/cyclocosm/info.json").json()
        return data['portrait_small']


if __name__ == '__main__':
    v = VimeoApi("cyclocosm")
    for video in v.videos_for_user():
        print video
    print v.icon()
