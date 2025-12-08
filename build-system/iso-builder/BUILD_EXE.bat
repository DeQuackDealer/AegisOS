@echo off
title Building Aegis ISO Builder Executables
color 0A

echo ============================================
echo   Aegis OS ISO Builder - Creating EXE Files
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Opening Python download page...
    start https://www.python.org/downloads/
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Install PyInstaller if needed
echo Installing/updating PyInstaller...
pip install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller
    pause
    exit /b 1
)
echo [OK] PyInstaller ready
echo.

REM Build Freemium version
echo Building Freemium Edition...
pyinstaller --onefile --noconsole --name "AegisBuilder-Freemium" aegis_freemium.py
if errorlevel 1 (
    echo [ERROR] Failed to build Freemium
    pause
    exit /b 1
)
echo [OK] Freemium built
echo.

REM Build Licensed version
echo Building Licensed Edition...
pyinstaller --onefile --noconsole --name "AegisBuilder-Licensed" aegis_licensed.py
if errorlevel 1 (
    echo [ERROR] Failed to build Licensed
    pause
    exit /b 1
)
echo [OK] Licensed built
echo.

REM Cleanup
echo Cleaning up...
rmdir /s /q build 2>nul
del *.spec 2>nul
echo.

echo ============================================
echo   BUILD COMPLETE!
echo ============================================
echo.
echo Your executables are in the "dist" folder:
echo   - AegisBuilder-Freemium.exe
echo   - AegisBuilder-Licensed.exe
echo.
echo These EXE files work WITHOUT Python installed!
echo Just double-click to run on any Windows PC.
echo.

explorer dist
pause
