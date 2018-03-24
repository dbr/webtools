import os
OUTPUT_DIR = os.getenv("YTDL_DOWNLOAD_PATH",
                       os.path.expanduser("/data/ytdl_downloads"))
OUTPUT_FORMAT = "%(uploader)s/%(upload_date)s_%(title)s__%(uploader)s_%(id)s.%(ext)s"
YOUTUBE_DL_FLAGS = ['--max-quality=22',]

DB_PATH = os.getenv("YTDL_DB_PATH",
    '/Users/dbr/code/webtools/dev.sqlite3')

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
