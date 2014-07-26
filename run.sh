session="webtools" # tmux session name
venv_name="webtools" # virtualenv name (e.g "workon webtools")

tmux has-session -t ${session} 2>/dev/null

if [ $? -ne 0 ]; then
    set -o errexit

    # Make new session, with cwd set to home
    pushd .
    cd ~
    tmux new-session -s ${session} -n server -d
    popd

    # Shell with virtualenv active
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m

    tmux select-layout tiled

    # HTTP server
    tmux split-window -v -t webtools
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m
    tmux send-keys -t webtools "python manage.py runserver 0.0.0.0:8001" C-m

    tmux select-layout tiled

    # Celery worker for default queue
    tmux split-window -v -t webtools
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m
    tmux send-keys -t webtools "python manage.py rqworker ytdl-default" C-m

    tmux select-layout tiled

    # Celery download worker
    tmux split-window -v -t webtools
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m
    tmux send-keys -t webtools "python manage.py rqworker ytdl-download" C-m

    tmux select-layout tiled

	# Periodic refresh
    tmux split-window -v -t webtools
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m
    tmux send-keys -t webtools "python manage.py ytdl_scheduler" C-m

    tmux select-layout even-vertical
    tmux select-pane -t webtools:1.0
fi

tmux attach-session
