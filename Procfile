web: python main.py server --host 0.0.0.0 --port 8008

task: env PYTHONUNBUFFERED=1 rqworker ytdl-default --url $REDIS_URL
taskdl: env PYTHONUNBUFFERED=1 rqworker ytdl-download --url $REDIS_URL

scheduler: env PYTHONUNBUFFERED=1 python main.py scheduler
