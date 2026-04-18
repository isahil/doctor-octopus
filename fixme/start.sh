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

if [ "$INITIALIZE" = "true" ]; then
    # echo "[$(date)] Initializing the app environment"
    # poetry run python3 initialize.py
    echo "[$(date)] Initialized the app environment"
fi

if [ "$SERVER_MODE" = "fixme" ]; then
    echo "[$(date)] Running fixme server"
    poetry run python3 server.py 2>&1 & FIXME_PID=$!
    echo $FIXME_PID > "${pid_dir}fixme.pid"
    echo "[$(date)] Fixme server parent process started with PID: $FIXME_PID"
else
    echo "[$(date)] Unknown server mode: $SERVER_MODE"
    echo "[$(date)] Supported modes: 'main', 'fixme', 'notification'"
    exit 1
fi
