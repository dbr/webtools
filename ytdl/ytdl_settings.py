import os
from django.conf import settings


OUTPUT_DIR = getattr(
    settings,
    "YTDL_OUTPUT_DIR", os.path.expanduser("~/Movies/ytdl"))
OUTPUT_FORMAT = getattr(
    settings,
    "OUTPUT_FORMAT", "%(upload_date)s_%(title)s_%(id)s.%(ext)s")
YOUTUBE_DL_FLAGS = getattr(
    settings,
    "YTDL_YOUTUBE_DL_FLAGS", [])
