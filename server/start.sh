echo "Starting the FASTAPI server"

OS_NAME=$(uname)
echo "OS: $OS_NAME"

if [ "$OS_NAME" = "Linux" ] || [ "$OS_NAME" = "Darwin" ]; then
    echo "Linux .venv activation"
    source $HOME/venv/bin/activate
else
    echo "Windows .venv activation"
    source $HOME/venv/Scripts/Activate
fi

uvicorn server:fastapi_app --host 0.0.0.0 --port 8000 --workers 3 --reload
