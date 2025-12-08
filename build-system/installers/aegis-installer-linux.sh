#!/bin/bash
#
# Aegis OS Installer - Linux Launcher
# Auto-installs dependencies and runs the Python installer
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_TYPE="${1:-freemium}"

echo "============================================"
echo "  Aegis OS Installer - Linux"
echo "============================================"
echo ""

# Check for Python 3
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        return 0
    elif command -v python &> /dev/null; then
        if python --version 2>&1 | grep -q "Python 3"; then
            PYTHON_CMD="python"
            return 0
        fi
    fi
    return 1
}

# Install Python if missing
install_python() {
    echo "Python 3 not found. Installing..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-tk
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip python3-tkinter
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm python python-pip tk
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y python3 python3-pip python3-tk
    else
        echo "ERROR: Could not detect package manager."
        echo "Please install Python 3 manually and run this script again."
        exit 1
    fi
}

# Install dependencies
install_deps() {
    echo "Installing Python dependencies..."
    $PYTHON_CMD -m pip install --user cryptography 2>/dev/null || \
    $PYTHON_CMD -m pip install cryptography 2>/dev/null || \
    pip3 install --user cryptography 2>/dev/null || \
    pip install --user cryptography
    echo "Dependencies installed."
}

# Check tkinter
check_tkinter() {
    if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
        echo "Installing tkinter..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y python3-tk
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-tkinter
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm tk
        fi
    fi
}

# Main
if ! check_python; then
    install_python
    check_python
fi

echo "Using: $($PYTHON_CMD --version)"
install_deps
check_tkinter

# Determine which installer to run
if [ "$INSTALLER_TYPE" = "licensed" ] || [ "$INSTALLER_TYPE" = "Licensed" ]; then
    INSTALLER="aegis-installer-licensed.py"
    echo "Starting Licensed installer..."
else
    INSTALLER="aegis-installer-freemium.py"
    echo "Starting Freemium installer..."
fi

if [ -f "$SCRIPT_DIR/$INSTALLER" ]; then
    $PYTHON_CMD "$SCRIPT_DIR/$INSTALLER"
else
    echo "ERROR: $INSTALLER not found in $SCRIPT_DIR"
    exit 1
fi
