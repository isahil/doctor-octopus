MODE=$1 # app, lite, e2e [app: all dependencies for the app, lite: only client/npm dependencies, e2e: all dependencies including playwright]
: "${MODE:=app}" # Default mode is app
START_TIME=$(date)
echo "Setting up Doctor Octopus in "$MODE" mode... [START TIME: $START_TIME]"
echo "Setting up the Root app directory..."
npm install
echo "Root app directory set up finished!"

if [ "$MODE" = "all" ] || [ "$MODE" = "app" ]; then
    echo "Setting up the Server..."
    cd server

    # Get the OS name to handle OS specific commands
    OS_NAME=$(uname)

    echo "Creating & activating the python virtual environment..."
    
    if [ "$OS_NAME" = "Linux" ] || [ "$OS_NAME" = "Darwin" ]; then
        python3 -m venv $HOME/venv
        source $HOME/venv/bin/activate
    elif [ "$OS_NAME" = "CYGWIN" ] || [ "$OS_NAME" = "MINGW" ] || [ "$OS_NAME" = "MSYS" ] || [ "$OS_NAME" = "MINGW64_NT-10.0-22631" ] || [ "$OS_NAME" = "MINGW64_NT-10.0-19045" ]; then
        python -m venv $HOME/venv
        source $HOME/venv/Scripts/Activate
    else
        echo "Unsupported OS: $OS_NAME"
        exit 1
    fi

    echo "Installing the server python dependencies..."
    pip install .
    echo "Server set up finished!"

    cd ..
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "app" ] || [ "$MODE" = "lite" ]; then
    echo "Setting up the Client..."
    cd client

    npm install
    echo "Client set up finished!"

    cd ..
fi

if [ "$MODE" = "all" ]; then
    echo "Setting up the Playwright project..."
    cd playwright
    npm install
    echo "Playwright set up finished!"
    cd ..
fi

END_TIME=$(date)
TIME_TAKEN=$(($(date -d "$END_TIME" +%s) - $(date -d "$START_TIME" +%s)))
echo "Finished setting up Doctor Octopus in "$MODE" mode! [TIME TAKEN: $TIME_TAKEN seconds, END TIME: $END_TIME]"
