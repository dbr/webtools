import requests
# For some reason, Vimeo ignores the "?page=2" parameter when requested by urllib/urllib2, but is okay with requests


class VimeoApi(object):
    def __init__(self, chanid):
        self.chanid = chanid

    def videos_for_user(self, limit=10):
        # For some bizarre reason, the API returns timestamps in
        # Eastern Timezone. WTF? http://vimeo.com/forums/topic:45607

        import dateutil.tz
        import dateutil.parser
        tz = dateutil.tz.gettz("US/Eastern")

        for page in range(3):
            page = page + 1
            url = "http://vimeo.com/api/v2/{chanid}/videos.json?page={page}".format(
                chanid = self.chanid,
                page = page)
            data = requests.get(url).json()
            for cur in data:
                dt = dateutil.parser.parse(cur['upload_date'])
                dt = dt.replace(tzinfo=tz)
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
        data = requests.get("http://vimeo.com/api/v2/%s/info.json" % self.chanid).json()
        return data['portrait_small']

    def title(self):
        data = requests.get("http://vimeo.com/api/v2/%s/info.json" % self.chanid).json()
        return data['display_name']


if __name__ == '__main__':
    v = VimeoApi("cyclocosm")
    for video in v.videos_for_user():
        print(video)
    print(v.icon())
