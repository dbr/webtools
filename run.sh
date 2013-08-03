session="webtools"
venv_name="youtube2"

tmux has-session -t ${session} 2>/dev/null

if [ $? -ne 0 ]; then
    # Make new session, with cwd set to home
    pushd .
    cd ~
    tmux new-session -s ${session} -n server -d
    popd

    # Shell with virtualenv active
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m

    # HTTP server
    tmux split-window -v -t webtools
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m
    tmux send-keys -t webtools "python manage.py runserver 0.0.0.0:8001" C-m

    # Celery worker
    tmux split-window -v -t webtools
    tmux send-keys -t webtools "cd '$(pwd)'" C-m
    tmux send-keys -t webtools "workon ${venv_name}" C-m
    tmux send-keys -t webtools "python manage.py celery worker" C-m

    tmux select-pane -t webtools:1.0
fi

tmux attach-session
