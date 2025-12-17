#!/bin/bash
# Build Aegis Media Creator into a standalone .exe
# Run this on a Windows machine with Python installed

echo "Building Aegis Media Creation Tool..."

# Install PyInstaller if not present
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile \
    --windowed \
    --name "Aegis Media Creator" \
    --icon="../assets/aegis-icon.ico" \
    --add-data "aegis-icon.ico;." \
    aegis-media-creator.py

echo "Done! Executable is in dist/Aegis Media Creator.exe"
