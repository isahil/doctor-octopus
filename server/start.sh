#!/bin/bash

START_TIME=$(date +%s)
SERVER_MODE=$1
INITIALIZE=$2
echo "[$(date)] Starting the $SERVER_MODE server service... pwd: $(pwd)"

pid_dir="../logs/"

if [ -z "$SERVER_MODE" ]; then
    echo "[$(date)] No server mode specified. Defaulting to 'main'."
    SERVER_MODE="main"
fi

# OS_NAME=$(uname)
# echo "[$(date)] OS: $OS_NAME"
# if [ "$OS_NAME" = "Linux" ] || [ "$OS_NAME" = "Darwin" ]; then
#     echo "[$(date)] Linux .venv activation"
#     source $HOME/venv/bin/activate
# else
#     echo "[$(date)] Windows .venv activation"
#     source $HOME/venv/Scripts/Activate
# fi

if [ "$SERVER_MODE" = "main" ]; then

    if [ "$INITIALIZE" = "true" ]; then
        echo "[$(date)] Initializing the app environment"
        poetry run python3 initialize.py
    fi

    echo "[$(date)] Running main server"
    poetry run python3 server.py 2>&1 & MAIN_PID=$!
    echo $MAIN_PID > "${pid_dir}server.pid"
    echo "[$(date)] Main server parent process started with PID: $MAIN_PID"
elif [ "$SERVER_MODE" = "fixme" ]; then
    echo "[$(date)] Running fixme server"
    poetry run python3 server-fixme.py 2>&1 & FIXME_PID=$!
    echo "[$(date)] Fixme server parent process started with PID: $FIXME_PID"
elif [ "$SERVER_MODE" = "notification" ]; then
    echo "[$(date)] Running notification service"
    poetry run python3 src/component/notification.py 2>&1 & NOTIFICATION_PID=$!
    echo $NOTIFICATION_PID > "${pid_dir}notification.pid"
    echo "[$(date)] Notification service started with PID: $NOTIFICATION_PID"
else
    echo "[$(date)] Unknown server mode: $SERVER_MODE"
    echo "[$(date)] Supported modes: 'main', 'fixme', 'notification'"
    exit 1
fi

# Alternative way to run the server
# if [ "$NODE_ENV" = "dev" ]; then
#     uvicorn server:fastapi_app --host 0.0.0.0 --port 8000 --workers 1 --reload
# else
#     uvicorn server:fastapi_app --host 0.0.0.0 --port 8000 --workers 2
# fi
