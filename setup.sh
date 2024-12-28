echo "Setting up the root project directory..."
ALL=$1

npm install
echo "Root project directory set up finished!"
echo "Setting up the server..."
cd server

# Get the OS name
OS_NAME=$(uname)

# Check the OS and activate the virtual environment accordingly
if [ "$OS_NAME" = "Linux" ] || [ "$OS_NAME" = "Darwin" ]; then
    # For Linux and macOS
    python3 -m venv $HOME/venv
    source $HOME/venv/bin/activate
elif [ "$OS_NAME" = "CYGWIN" ] || [ "$OS_NAME" = "MINGW" ] || [ "$OS_NAME" = "MSYS" ] || [ "$OS_NAME" = "MINGW64_NT-10.0-22631" ]; then
    # For Windows (Cygwin, MinGW, Git Bash)
    python -m venv $HOME/venv
    source $HOME/venv/Scripts/Activate
else
    echo "Unsupported OS: $OS_NAME"
    exit 1
fi

pip install .
echo "Server set up finished!"

cd ../client

echo "Setting up the client..."
npm install
echo "Client set up finished!"

if [ "$ALL" = "true" ]; then
    echo "Setting up the playwright project..."
    cd ../playwright
    npm install
    echo "Playwright set up finished!"
fi

cd ..
echo "Setup finished!"
