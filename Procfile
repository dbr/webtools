web: python main.py server --host 0.0.0.0 --port 8008

task: env PYTHONUNBUFFERED=1 rqworker ytdl-default --host $REDIS_HOST --port $REDIS_PORT
taskdl: env PYTHONUNBUFFERED=1 rqworker ytdl-download --host $REDIS_HOST --port $REDIS_PORT

scheduler: env PYTHONUNBUFFERED=1 python main.py scheduler
