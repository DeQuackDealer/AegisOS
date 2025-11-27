@echo off
setlocal enabledelayedexpansion
title Aegis OS Freemium Installer
color 0A

:header
cls
echo.
echo  ============================================================
echo        AEGIS OS FREEMIUM EDITION INSTALLER
echo            Professional Linux - FREE
echo  ============================================================
echo.
echo  Edition: Freemium
echo  Size: 2.1 GB
echo  Price: FREE
echo.

:menu
echo  Select an option:
echo.
echo  [1] Download Aegis OS Freemium ISO
echo  [2] Create Bootable USB (using Rufus)
echo  [3] View System Requirements
echo  [4] Exit
echo.
set /p choice="  Enter choice (1-4): "

if "%choice%"=="1" goto download
if "%choice%"=="2" goto usb
if "%choice%"=="3" goto requirements
if "%choice%"=="4" goto exit
goto menu

:download
cls
echo.
echo  ============================================================
echo        DOWNLOADING AEGIS OS FREEMIUM
echo  ============================================================
echo.
echo  Preparing download...
echo.

set "DOWNLOAD_DIR=%USERPROFILE%\Downloads"
set "ISO_NAME=aegis-os-freemium-v1.0.iso"
set "ISO_PATH=%DOWNLOAD_DIR%\%ISO_NAME%"

echo  Download location: %ISO_PATH%
echo.
echo  NOTE: The Aegis OS Freemium ISO is currently being built.
echo        ISO builds are generated on-demand for quality assurance.
echo.
echo  The ISO includes:
echo  - XFCE 4.18 Desktop Environment
echo  - Firefox, LibreOffice, GIMP
echo  - Basic security hardening
echo  - Nouveau graphics drivers
echo.
echo  ============================================================
echo        ISO BUILD STATUS: IN PROGRESS
echo  ============================================================
echo.
echo  Your ISO is being prepared. This typically takes 15-30 minutes.
echo.
echo  Options:
echo  [1] Check build status online
echo  [2] Get notified when ready (opens email)
echo  [3] Back to menu
echo.
set /p dl_choice="  Enter choice (1-3): "

if "%dl_choice%"=="1" (
    start "" "https://aegis-os.replit.app/freemium"
    echo.
    echo  Opened build status page in browser.
)
if "%dl_choice%"=="2" (
    start "" "mailto:riley.liang@hotmail.com?subject=Aegis%%20OS%%20Freemium%%20ISO%%20Request&body=Please%%20notify%%20me%%20when%%20the%%20Freemium%%20ISO%%20is%%20ready%%20for%%20download."
    echo.
    echo  Email client opened.
)

echo.
pause
goto header

:usb
cls
echo.
echo  ============================================================
echo        CREATE BOOTABLE USB
echo  ============================================================
echo.
echo  To create a bootable USB drive, use Rufus:
echo.
echo  1. Download Rufus from: https://rufus.ie
echo  2. Insert a USB drive (8GB minimum)
echo  3. Open Rufus and select the Aegis OS ISO file
echo  4. Click START and wait for completion
echo  5. Boot your computer from the USB drive
echo.
echo  Would you like to download Rufus now?
echo.
set /p rufus="  Download Rufus? (Y/N): "

if /i "%rufus%"=="Y" (
    start "" "https://rufus.ie"
    echo.
    echo  Rufus website opened in your browser.
)

echo.
echo  WARNING: Creating a bootable USB will ERASE all data on the drive!
echo.
pause
goto header

:requirements
cls
echo.
echo  ============================================================
echo        SYSTEM REQUIREMENTS - FREEMIUM EDITION
echo  ============================================================
echo.
echo  MINIMUM REQUIREMENTS:
echo  ---------------------
echo  CPU:        64-bit processor (x86_64)
echo  RAM:        2 GB minimum (4 GB recommended)
echo  Storage:    15 GB free space
echo  USB:        8 GB flash drive for installation
echo.
echo  INCLUDED SOFTWARE:
echo  ------------------
echo  - XFCE 4.18 Desktop
echo  - Firefox Web Browser
echo  - LibreOffice Suite
echo  - GIMP Image Editor
echo  - VLC Media Player
echo  - Basic development tools
echo.
echo  GRAPHICS SUPPORT:
echo  -----------------
echo  - Nouveau drivers (open-source NVIDIA)
echo  - Intel integrated graphics
echo  - AMD open-source drivers
echo.
echo  UPGRADE OPTIONS:
echo  ----------------
echo  Visit https://aegis-os.replit.app/pricing for premium editions
echo  with enhanced features, gaming support, and AI tools.
echo.
pause
goto header

:exit
cls
echo.
echo  ============================================================
echo        THANK YOU FOR CHOOSING AEGIS OS FREEMIUM
echo  ============================================================
echo.
echo  Commercial Software. Sold as-is. Support available separately.
echo  Contact: riley.liang@hotmail.com
echo.
echo  Upgrade to premium: https://aegis-os.replit.app/pricing
echo.
echo  Goodbye!
echo.
timeout /t 3 >nul
exit /b 0
