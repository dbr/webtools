web: python main.py server --host 0.0.0.0

task: env PYTHONUNBUFFERED=1 rqworker ytdl-default
taskdl: env PYTHONUNBUFFERED=1 rqworker ytdl-download

scheduler: env PYTHONUNBUFFERED=1 python main.py scheduler
