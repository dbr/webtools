import os
from django.conf import settings


OUTPUT_DIR = os.path.expanduser("~/Movies/ytdl")
OUTPUT_FORMAT = "%(upload_date)s_%(title)s_%(id)s.%(ext)s"
