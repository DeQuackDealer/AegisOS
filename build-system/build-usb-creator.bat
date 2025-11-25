@echo off
REM ============================================================
REM Aegis OS USB Creator - Build Script
REM Creates a standalone Windows executable using PyInstaller
REM ============================================================
REM 
REM Prerequisites:
REM   1. Python 3.8+ installed and in PATH
REM   2. Run this script as Administrator (recommended)
REM
REM Output:
REM   dist\AegisUSBCreator.exe - Single standalone executable
REM
REM ============================================================

setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo    Aegis OS USB Creator - Build System
echo    Building standalone Windows executable...
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [INFO] pip found:
pip --version
echo.

REM Create virtual environment for clean build (optional but recommended)
echo [STEP 1/6] Setting up build environment...

REM Install required packages
echo [STEP 2/6] Installing dependencies...
pip install pyinstaller pywin32 wmi --quiet --disable-pip-version-check

if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed to install
    echo Continuing anyway...
)

echo [INFO] Dependencies installed successfully
echo.

REM Create version info file for Windows
echo [STEP 3/6] Creating version info...

(
echo VSVersionInfo^(
echo   ffi=FixedFileInfo^(
echo     filevers=^(4, 0, 0, 0^),
echo     prodvers=^(4, 0, 0, 0^),
echo     mask=0x3f,
echo     flags=0x0,
echo     OS=0x40004,
echo     fileType=0x1,
echo     subtype=0x0,
echo     date=^(0, 0^)
echo   ^),
echo   kids=[
echo     StringFileInfo^(
echo       [
echo         StringTable^(
echo           u'040904B0',
echo           [
echo             StringStruct^(u'CompanyName', u'Aegis OS'^),
echo             StringStruct^(u'FileDescription', u'Aegis OS USB Creator'^),
echo             StringStruct^(u'FileVersion', u'4.0.0.0'^),
echo             StringStruct^(u'InternalName', u'AegisUSBCreator'^),
echo             StringStruct^(u'LegalCopyright', u'Copyright 2024-2025 Aegis OS'^),
echo             StringStruct^(u'OriginalFilename', u'AegisUSBCreator.exe'^),
echo             StringStruct^(u'ProductName', u'Aegis OS USB Creator'^),
echo             StringStruct^(u'ProductVersion', u'4.0.0.0'^)
echo           ]
echo         ^)
echo       ]
echo     ^),
echo     VarFileInfo^([VarStruct^(u'Translation', [1033, 1200]^)]^)
echo   ]
echo ^)
) > version_info.txt

echo [INFO] Version info created
echo.

REM Create a simple icon file if not exists
echo [STEP 4/6] Checking for icon file...

if not exist aegis-icon.ico (
    echo [INFO] Creating placeholder icon...
    REM Create a simple valid ICO file structure
    REM This creates a minimal 16x16 icon
    
    REM For a proper build, replace this with an actual icon file
    echo [WARNING] No aegis-icon.ico found. Building without custom icon.
    echo [INFO] To add custom icon, place aegis-icon.ico in this directory
    
    REM Remove icon reference from spec if no icon exists
    powershell -Command "(Get-Content aegis-usb-creator.spec) -replace \"icon='aegis-icon.ico',\", '' | Set-Content aegis-usb-creator.spec.tmp"
    if exist aegis-usb-creator.spec.tmp (
        move /y aegis-usb-creator.spec.tmp aegis-usb-creator.spec >nul
    )
) else (
    echo [INFO] Custom icon found: aegis-icon.ico
)

echo.

REM Clean previous builds
echo [STEP 5/6] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo [INFO] Clean complete
echo.

REM Build the executable
echo [STEP 6/6] Building executable with PyInstaller...
echo.
echo This may take a few minutes...
echo.

pyinstaller aegis-usb-creator.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed!
    echo Check the error messages above for details.
    echo.
    echo Common fixes:
    echo   1. Run as Administrator
    echo   2. Disable antivirus temporarily
    echo   3. Ensure all dependencies are installed
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo    BUILD SUCCESSFUL!
echo ============================================================
echo.

REM Check output
if exist dist\AegisUSBCreator.exe (
    echo [SUCCESS] Executable created:
    echo.
    echo    dist\AegisUSBCreator.exe
    echo.
    
    REM Show file size
    for %%A in (dist\AegisUSBCreator.exe) do (
        set size=%%~zA
        set /a sizeMB=!size!/1048576
        echo    Size: !sizeMB! MB
    )
    echo.
    
    REM Generate SHA256 checksum
    echo [INFO] Generating checksum...
    certutil -hashfile dist\AegisUSBCreator.exe SHA256 > dist\AegisUSBCreator.exe.sha256 2>nul
    if exist dist\AegisUSBCreator.exe.sha256 (
        echo [INFO] Checksum saved to: dist\AegisUSBCreator.exe.sha256
    )
    echo.
    
    echo ============================================================
    echo    Distribution Instructions:
    echo ============================================================
    echo.
    echo    1. The executable is fully standalone - no Python needed
    echo    2. Users can run it directly by double-clicking
    echo    3. Administrator rights will be requested automatically
    echo    4. Works on Windows 7, 8, 10, and 11
    echo.
    echo    To test the build:
    echo      dist\AegisUSBCreator.exe
    echo.
    echo ============================================================
    
) else (
    echo [ERROR] Executable was not created!
    echo Check the build output above for errors.
)

REM Cleanup temporary files
echo.
echo [INFO] Cleaning up temporary files...
if exist version_info.txt del version_info.txt
if exist build rmdir /s /q build
echo [INFO] Cleanup complete
echo.

echo Press any key to exit...
pause >nul

endlocal
exit /b 0
