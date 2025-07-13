#!/bin/bash
START_TIME=$(date +%s)
echo "[$(date)] Starting the FASTAPI server"

SERVER_MODE=$1

if [ -z "$SERVER_MODE" ]; then
    echo "[$(date)] No server mode specified. Defaulting to 'main'."
    SERVER_MODE="main"
fi

OS_NAME=$(uname)
echo "[$(date)] OS: $OS_NAME"

if [ "$OS_NAME" = "Linux" ] || [ "$OS_NAME" = "Darwin" ]; then
    echo "[$(date)] Linux .venv activation"
    source $HOME/venv/bin/activate
else
    echo "[$(date)] Windows .venv activation"
    source $HOME/venv/Scripts/Activate
fi

if [ "$SERVER_MODE" = "main" ]; then
    echo "[$(date)] Started setting up the app environment"
    python initialize.py
    echo "[$(date)] Finished setting up the app environment"

    echo "[$(date)] Running main server"
    python server.py
else
    echo "[$(date)] Running util server"
    python server-util.py
fi

# alternative way to run the server
# if [ "$NODE_ENV" = "dev" ]; then
#     uvicorn server:fastapi_app --host 0.0.0.0 --port 8000 --workers 1 --reload
# else
#     uvicorn server:fastapi_app --host 0.0.0.0 --port 8000 --workers 2
# fi
