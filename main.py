import os
import sys
import time
import json
import datetime


def _scheduler_run(on_start):
    import ytdl.tasks
    minutes = 20

    first_run = True
    while True:
        if not on_start or not first_run:
            print("%s Sleeping %s minutes" % (datetime.datetime.now(), minutes))
            time.sleep(60*minutes)
        first_run = False

        print("%s Refreshing!" % datetime.datetime.now())
        ytdl.tasks.refresh_all_channels()


def scheduler(on_start):
    try:
        return _scheduler_run(on_start=on_start)
    except KeyboardInterrupt:
        return


def refresh(limit, all, filter):
    import ytdl.models
    channels = ytdl.models.Channel.select()
    for c in channels:
        if filter is not None and filter not in c.title.lower():
            continue
        print("Force-refreshing %s" % c)
        if all:
            c.grab(limit=limit, stop_on_existing=False)
        else:
            c.grab(limit=limit)


def dedupe(kill):
    import ytdl.models

    if not kill:
        print("Dry-run, specify --kill to delete dupes")

    seen = set()
    for video in ytdl.models.Video.select():
        # TODO: maybe only check for dupes in channel? Utterly unlikely
        url = video.url
        if url in seen:
            if kill:
                print("Deleting dupe %s (%s on %s)" % (url, video.status, video.channel.title))
                video.delete_instance()
            else:
                print("Dupe %s (%s on %s)" % (url, video.status, video.channel.title))
        else:
            seen.add(url)

def cleanup():
    """Deletes videos where the associated channel no longer exists
    """
    import ytdl.models
    for v in ytdl.models.Video.select():
        try:
            assert v.channel
        except ytdl.models.Channel.DoesNotExist:
            print("Deleting orphaned video '%s'" % v.title)
            v.delete_instance()

def backup(filename):
    if filename is None:
        f = sys.stdout
    else:
        f = open(filename +  ".tmp", "w+")


    import ytdl.models

    channels = []
    for c in ytdl.models.Channel.select():
        chaninfo = {'chanid': c.chanid,
                    'service': c.service,
                    'videos': []
                }
        for v in ytdl.models.Video.select().where(ytdl.models.Video.channel == c):
            chaninfo['videos'].append(
                {'title': v.title,
                 'url': v.url,
                 'videoid': v.videoid,
                 'status': v.status,
                 'publishdate': v.status,
                 'service': c.service,
             })

        channels.append(chaninfo)

    json.dump(channels, f,
              sort_keys=True, indent=1, separators=(',', ': '))
    f.write("\n") # Trailing new line in file (or stdout)

    if filename is not None:
        os.rename(filename +  ".tmp", filename)


def restore(filename):
    if filename is None:
        f = sys.stdin
    else:
        f = open(filename)

    import ytdl.models

    with ytdl.models.database.transaction():
        all_chan = json.load(f)
        for channel in all_chan:
            db_chan = ytdl.models.Channel.get(chanid=channel['chanid'])
            if db_chan is None:
                print("Creating %s (service %s)" % (channel['chanid'], channel['service']))
                db_chan = ytdl.models.Channel(chanid = channel['chanid'], service=channel['service'])
                db_chan.save()

            # Get videos form channel
            print("Getting videos for %s" % (db_chan))
            db_chan.grab()

            # Restore statuses
            print("Restore statuses")
            for video in channel['videos']:
                v = ytdl.models.Video.get(videoid=video['videoid'])
                if v is None:
                    print("%s does not exist (title: %s)" % (video['videoid'], video['title']))
                    continue # Next video
                v.status = video['status']
                v.save()



def server(port, host):
    from ytdl.app import app
    app.debug=True
    app.run(host=host, port=port)


def dbinit():
    import ytdl.models
    ytdl.models.database.connect()
    ytdl.models.Channel.create_table()
    ytdl.models.Video.create_table()


if __name__ == '__main__':
    import argparse
    p_main = argparse.ArgumentParser()
    subparsers = p_main.add_subparsers()

    p_server = subparsers.add_parser('server')
    p_server.add_argument('-o', '--host', default='0.0.0.0')
    p_server.add_argument('-p', '--port', default=8008, type=int)
    p_server.set_defaults(func=server)

    p_server = subparsers.add_parser('dbinit')
    p_server.set_defaults(func=dbinit)

    p_refresh = subparsers.add_parser('refresh')
    p_refresh.set_defaults(func=refresh)
    p_refresh.add_argument("-a", "--all", action="store_true", help="don't stop because a video exists (check for older videos)")
    p_refresh.add_argument("--limit", type=int, default=1000, help="maximum number of videos to try and grab (default %(default)s)")
    p_refresh.add_argument("-f", "--filter", default=None, help="only refresh channels matching this (simple case-insensetive string-matching on channel title)")


    p_dedupe = subparsers.add_parser('dedupe')
    p_dedupe.set_defaults(func=dedupe)
    p_dedupe.add_argument('--kill', default=False, action="store_true")

    p_scheduler = subparsers.add_parser('scheduler')
    p_scheduler.set_defaults(func=scheduler)
    p_scheduler.add_argument('--on-start', action="store_true", help="perform refresh immediately (instead of after delay)")

    p_backup = subparsers.add_parser('backup')
    p_backup.set_defaults(func=backup)
    p_backup.add_argument("-f", "--filename", default=None)

    p_restore = subparsers.add_parser('restore')
    p_restore.set_defaults(func=restore)
    p_restore.add_argument("-f", "--filename", default=None)

    p_cleanup = subparsers.add_parser('cleanup')
    p_cleanup.set_defaults(func=cleanup)

    args = p_main.parse_args()
    func = args.func
    args = {k:v for k, v in vars(args).items() if k != 'func'}
    func(**args)
