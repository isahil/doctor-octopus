#!/bin/bash
MODE=$1 # app/lite/all
# app: client & server dependencies
# lite: only client dependencies.
# all: client, server, e2e [playwright & pytest] dependencies. It'll also run server os setup steps.
: "${MODE:=app}" # Default mode is app

START_TIME=$(date +%s)
echo "Setting up Doctor Octopus in \""$MODE"\" mode. START TIME: [$(date)]"
WORK_DIR=$(pwd)

if [ "$MODE" = "all" ]; then
    sh utils/setup-server.sh
fi

echo "Setting up the Root app directory..."

mkdir logs server/test_reports e2e/logs e2e/test_reports
touch logs/doc.log e2e/logs/the-lab.log
echo "Created the logs & test_reports directories & files"

npm install
echo "Root app directory set up finished!"

if [ "$MODE" = "all" ] || [ "$MODE" = "app" ]; then
    echo "Setting up the Server..."
    cd server

    # Get the OS name to handle OS specific commands
    # OS_NAME=$(uname)
    # echo "Creating & activating the python virtual environment..."
    # if [ "$OS_NAME" = "Linux" ] || [ "$OS_NAME" = "Darwin" ]; then
    #     echo "[$(date)] installing pipx and poetry package manager."
    #     pip3 install pipx poetry # Install pipx and poetry globally
    #     python3 -m venv $HOME/venv
    #     . $HOME/venv/bin/activate
    # elif [ "$OS_NAME" = "CYGWIN" ] || [ "$OS_NAME" = "MINGW" ] || [ "$OS_NAME" = "MSYS" ] || [ "$OS_NAME" = "MINGW64_NT-10.0-22631" ] || [ "$OS_NAME" = "MINGW64_NT-10.0-19045" ]; then
    #     echo "[$(date)] installing pipx and poetry package manager."
    #     pip install pipx poetry
    #     python -m venv $HOME/venv
    #     source $HOME/venv/Scripts/Activate
    # else
    #     echo "Unsupported OS: $OS_NAME"
    #     exit 1
    # fi

    echo "Installing the server poetry python dependencies..."
    poetry install
    echo "Server set up finished!"
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "app" ] || [ "$MODE" = "lite" ]; then
    echo "Setting up the Client..."
    cd $WORK_DIR/client
    npm install
    echo "Client set up finished!"
fi

if [ "$MODE" = "all" ]; then
    echo "Setting up the e2e test environment..."
    echo "Setting up the Playwright dependencies..."
    cd $WORK_DIR/e2e
    npm install
    echo "Setting up the PyTest dependencies..."
    poetry install
    echo "e2e test environment set up finished!"
    cd $WORK_DIR
fi

END_TIME=$(date +%s)
TIME_TAKEN=$(($END_TIME - $START_TIME))

echo "git: $(git --version)"
echo "node: $(node --version)"
echo "npm: $(npm --version)"
echo "python3: $(python3 --version)"
echo "python: $(python --version)"
echo "pip3: $(pip3 --version)"
echo "pip: $(pip --version)"
echo "venv: $(python3 -m venv --help | head -n 1)"
echo "Git, venv and Node.js $NODE_VERSION are installed."

echo "Finished setting up Doctor Octopus in \""$MODE"\" mode! | TIME TAKEN: $TIME_TAKEN second/s | END TIME: [$(date)]"
