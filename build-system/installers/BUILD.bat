@echo off
title Aegis OS Installer Builder
color 0A

echo.
echo ================================================================
echo   AEGIS OS INSTALLER BUILDER
echo ================================================================
echo.
echo   This will compile the Python installers into Windows .exe files.
echo.
echo   Requirements:
echo     - Python 3.8 or newer (will check automatically)
echo     - PyInstaller (will install automatically if missing)
echo.
echo ================================================================
echo.
pause

echo.
echo Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found!
echo.
echo Starting build process...
echo.

python "%~dp0build-all-installers.py"

echo.
pause
