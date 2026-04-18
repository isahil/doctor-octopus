#!/bin/bash
echo "Setting up the server machine with required tools. START TIME: [$(date)]"

# Get the OS name to handle OS specific commands
OS_NAME=$(uname)
echo "Detected OS: $OS_NAME"
NODE_VERSION="23"
SERVER_PY_VERSION="3.9"
FIXME_PY_VERSION="3.9"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

py_command="
if [ "$OS_NAME" = "Linux" ]; then
    py_command="python3"
elif [ "$OS_NAME" = "Darwin" ]; then
    py_command="python3"
elif [[ "$OS_NAME" == *"MINGW"* ]] || [[ "$OS_NAME" == *"MSYS"* ]]; then
    py_command="python"
else
    echo "Unsupported OS: $OS_NAME"
    exit 1
fi
echo "Using Python command: $py_command"


echo "Checking for required Python executables: python$SERVER_PY_VERSION and python$FIXME_PY_VERSION..."

# Build list of missing python versions
MISSING_PYS=()
for ver in "$SERVER_PY_VERSION" "$FIXME_PY_VERSION"; do
    py_exe="python${ver}"
    if ! command_exists "$py_exe"; then
        MISSING_PYS+=("$ver")
    fi
done

if [ ${#MISSING_PYS[@]} -eq 0 ]; then
    echo "All required Python versions are already installed. Skipping installation."
else
    echo "Missing Python versions detected: ${MISSING_PYS[*]}"
    INSTALL_FAILED=0
    if [ "$OS_NAME" = "Darwin" ]; then
        brew update
        for ver in "${MISSING_PYS[@]}"; do
            echo "Installing python@$ver via Homebrew..."
            brew install "python@${ver}"
            if [ $? -ne 0 ]; then
                INSTALL_FAILED=1
            fi
        done
    elif [ "$OS_NAME" = "Linux" ]; then
        sudo apt-get update
        for ver in "${MISSING_PYS[@]}"; do
            echo "Installing python$ver and venv/dev packages via apt..."
            sudo apt-get install -y "python${ver}" "python${ver}-venv" "python${ver}-dev"
            if [ $? -ne 0 ]; then
                INSTALL_FAILED=1
            fi
        done
    elif [[ "$OS_NAME" == *"MINGW"* ]] || [[ "$OS_NAME" == *"MSYS"* ]]; then
        for ver in "${MISSING_PYS[@]}"; do
            echo "Installing Python $ver via winget..."
            winget install --id "Python.Python.$ver" -e
            if [ $? -ne 0 ]; then
                INSTALL_FAILED=1
            fi
        done
    else
        echo "Unsupported OS for automated Python installation: $OS_NAME"
        INSTALL_FAILED=1
    fi

    if [ "$INSTALL_FAILED" -ne 0 ]; then
        echo "One or more Python installations failed. Install manually from https://www.python.org/downloads/ and press Enter to continue..."
        read -r
    else
        echo "Python installation(s) completed successfully."
    fi
fi

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

if ! command_exists artillery; then
    echo "Artillery not found. Installing Artillery globally using npm..."
    npm install -g artillery

    if [ $? -ne 0 ]; then
        echo "Failed to install Artillery. Exiting."
        exit 1
    fi
fi


if ! $py_command -m venv --help &> /dev/null || ! command_exists pip; then
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

echo "[$(date)] installing python poetry package manager using curl & $py_command."
curl -sSL 'https://install.python-poetry.org' | $py_command -
echo "If OS is Windows, ensure that Poetry's bin directory [%APPDATA%\Python\Scripts] is added to your PATH environment variable. You may need to restart your terminal/device for changes to take effect."

if [ ${PIPESTATUS[0]} -ne 0 ] || [ ${PIPESTATUS[1]} -ne 0 ]; then
    echo "Poetry installer failed. Install manually from https://python-poetry.org/docs/#installing-with-the-official-installer. Press Enter when done to continue..."
    read -r
else
    echo "Poetry installed successfully."
fi
