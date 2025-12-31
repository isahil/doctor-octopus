#!/bin/bash
echo "Setting up the server machine with required tools. START TIME: [$(date)]"

# Get the OS name to handle OS specific commands
OS_NAME=$(uname)
echo "Detected OS: $OS_NAME"
NODE_VERSION="23"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Git and Node.js if not already installed
echo "Checking for Git and Node.js..."

if ! command_exists git; then
    echo "Git not found. Installing Git..."
    
    if [ "$OS_NAME" = "Linux" ]; then
        # For Linux (Debian/Ubuntu-based)
        sudo apt-get update
        sudo apt-get install -y git
    elif [ "$OS_NAME" = "Darwin" ]; then
        # For macOS
        if command_exists brew; then
            brew install git
        else
            echo "Homebrew not found. Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OS_NAME" == *"MINGW"* ]] || [[ "$OS_NAME" == *"MSYS"* ]]; then
        # For Windows
        echo "Please download and install Git from https://git-scm.com/download/win"
        echo "Press Enter when Git is installed to continue..."
        read -r
    else
        echo "Unsupported OS for automated Git installation: $OS_NAME"
        echo "Please install Git manually and run this script again."
        exit 1
    fi
fi

if ! command_exists node || ! command_exists npm; then
    echo "Node.js/npm not found. Installing Node.js $NODE_VERSION..."
    
    if [ "$OS_NAME" = "Linux" ]; then
        # For Linux (Using NodeSource repository for Node.js $NODE_VERSION)
        curl -fsSL "https://deb.nodesource.com/setup_$NODE_VERSION.x" | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [ "$OS_NAME" = "Darwin" ]; then
        # For macOS
        if command_exists brew; then
            brew install node@"$NODE_VERSION"
        else
            echo "Homebrew not found. Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OS_NAME" == *"MINGW"* ]] || [[ "$OS_NAME" == *"MSYS"* ]]; then
        # For Windows
        echo "Please download and install Node.js 23 LTS from https://nodejs.org/en/download/"
        echo "Press Enter when Node.js is installed to continue..."
        read -r
    else
        echo "Unsupported OS for automated Node.js installation: $OS_NAME"
        echo "Please install Node.js manually and run this script again."
        exit 1
    fi
fi


if ! python3 -m venv --help &> /dev/null || ! command_exists pip; then
    echo "Python venv module is not installed!"
    
    if [ "$OS_NAME" = "Linux" ]; then
        echo "Installing python3-venv..."
        sudo apt-get update
        sudo apt-get install -y python3-venv
        sudo apt install python3-pip -y
    elif [ "$OS_NAME" = "Darwin" ]; then
        echo "Python on macOS should already have venv. If not, reinstall Python."
    else
        echo "Please install the Python venv module manually and run this script again."
        exit 1
    fi
fi

echo "[$(date)] installing python poetry package manager using curl."
curl -sSL 'https://install.python-poetry.org' | python -

if [ ${PIPESTATUS[0]} -ne 0 ] || [ ${PIPESTATUS[1]} -ne 0 ]; then
    echo "Poetry installer failed. Exiting."
    exit 1
else
    echo "Poetry installed successfully."
fi
