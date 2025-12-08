#!/bin/bash
#
# Aegis OS Installer - macOS Launcher
# Double-click to run, or run from Terminal
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "  Aegis OS Installer - macOS"
echo "============================================"
echo ""

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Python 3 not found."
    echo ""
    echo "Please install Python 3 from:"
    echo "  https://www.python.org/downloads/macos/"
    echo ""
    echo "Or using Homebrew:"
    echo "  brew install python3 python-tk"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Using: $($PYTHON_CMD --version)"

# Install cryptography if needed
if ! $PYTHON_CMD -c "import cryptography" 2>/dev/null; then
    echo "Installing cryptography..."
    $PYTHON_CMD -m pip install --user cryptography
fi

# Check tkinter
if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo ""
    echo "ERROR: tkinter not available."
    echo "Install with: brew install python-tk"
    read -p "Press Enter to exit..."
    exit 1
fi

# Ask which installer
echo ""
echo "Which edition would you like to install?"
echo "  1) Freemium (Free)"
echo "  2) Licensed (Paid editions)"
echo ""
read -p "Enter choice [1]: " choice

if [ "$choice" = "2" ]; then
    INSTALLER="aegis-installer-licensed.py"
else
    INSTALLER="aegis-installer-freemium.py"
fi

if [ -f "$INSTALLER" ]; then
    $PYTHON_CMD "$INSTALLER"
else
    echo "ERROR: $INSTALLER not found"
    read -p "Press Enter to exit..."
    exit 1
fi
