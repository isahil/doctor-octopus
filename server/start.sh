#!/bin/bash
echo "Starting the FASTAPI server"

MODE=$1
if [ -z "$MODE" ]; then
    echo "No mode specified. Defaulting to 'dev'."
    MODE="dev"
fi
echo "Running DO app in $MODE mode"

OS_NAME=$(uname)
echo "OS: $OS_NAME"

if [ "$OS_NAME" = "Linux" ] || [ "$OS_NAME" = "Darwin" ]; then
    echo "Linux .venv activation"
    source $HOME/venv/bin/activate
else
    echo "Windows .venv activation"
    source $HOME/venv/Scripts/Activate
fi

python setup.py

python server.py

# alternative way to run the server
# if [ "$MODE" = "dev" ]; then
#     uvicorn server:fastapi_app --host 0.0.0.0 --port 8000 --workers 1 --reload
# else
#     uvicorn server:fastapi_app --host 0.0.0.0 --port 8000 --workers 2
# fi
