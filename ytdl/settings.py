import os
OUTPUT_DIR = os.path.expanduser("~/Movies/ytdl")
OUTPUT_FORMAT = "%(upload_date)s_%(title)s__%(uploader)s_%(id)s.%(ext)s"
YOUTUBE_DL_FLAGS = ['--max-quality=22',]

DB_PATH = os.getenv("YTDL_DB_PATH",
    '/Users/dbr/code/webtools/dev.sqlite3')
