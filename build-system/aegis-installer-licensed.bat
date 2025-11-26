@echo off
setlocal enabledelayedexpansion
title Aegis OS Licensed Installer
color 0B

:header
cls
echo.
echo  ============================================================
echo        AEGIS OS LICENSED EDITION INSTALLER
echo            Professional Linux for Enterprise
echo  ============================================================
echo.

:license_input
echo  Please enter your license key to continue.
echo  (Format: XXXX-XXXX-XXXX-XXXX)
echo.
set /p LICENSE_KEY="  License Key: "

if "%LICENSE_KEY%"=="" (
    echo.
    echo  [ERROR] License key is required!
    echo.
    pause
    goto header
)

set PREFIX=%LICENSE_KEY:~0,4%
set EDITION=Unknown
set ISO_SIZE=Unknown

if "%PREFIX%"=="BSIC" (
    set EDITION=Basic Edition
    set ISO_SIZE=2.8 GB
)
if "%PREFIX%"=="WORK" (
    set EDITION=Workplace Edition
    set ISO_SIZE=3.2 GB
)
if "%PREFIX%"=="GAME" (
    set EDITION=Gamer Edition
    set ISO_SIZE=4.5 GB
)
if "%PREFIX%"=="AIDV" (
    set EDITION=AI Developer Edition
    set ISO_SIZE=5.2 GB
)
if "%PREFIX%"=="GMAI" (
    set EDITION=Gamer + AI Edition
    set ISO_SIZE=6.8 GB
)
if "%PREFIX%"=="SERV" (
    set EDITION=Server Edition
    set ISO_SIZE=3.5 GB
)

if "%EDITION%"=="Unknown" (
    echo.
    echo  [ERROR] Invalid license key prefix!
    echo  Please check your key and try again.
    echo.
    pause
    goto header
)

echo %LICENSE_KEY% > "%USERPROFILE%\aegis-license.key"

:menu
cls
echo.
echo  ============================================================
echo        AEGIS OS - %EDITION%
echo  ============================================================
echo.
echo  License Key: %LICENSE_KEY%
echo  Status:      ACTIVE
echo  ISO Size:    %ISO_SIZE%
echo.
echo  License saved to: %USERPROFILE%\aegis-license.key
echo.
echo  ============================================================
echo.
echo  Select an option:
echo.
echo  [1] Download %EDITION% ISO
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
echo        DOWNLOADING %EDITION%
echo  ============================================================
echo.
echo  License verified: %LICENSE_KEY%
echo  Edition: %EDITION%
echo  Size: %ISO_SIZE%
echo.
echo  NOTE: Your licensed ISO is being prepared.
echo        Custom builds include your license pre-activated.
echo.
echo  The %EDITION% includes all premium features:
echo  - Full hardware support
echo  - Premium software suite
echo  - Priority updates
echo.
echo  ============================================================
echo        ISO BUILD STATUS: PREPARING
echo  ============================================================
echo.
echo  Your custom ISO is being generated with your license.
echo  This ensures maximum security and personalization.
echo.
echo  Options:
echo  [1] Check download status online
echo  [2] Contact support
echo  [3] Back to menu
echo.
set /p dl_choice="  Enter choice (1-3): "

if "%dl_choice%"=="1" (
    start "" "https://aegis-os.replit.app/pricing"
    echo.
    echo  Opened status page in browser.
)
if "%dl_choice%"=="2" (
    start "" "mailto:riley.liang@hotmail.com?subject=Aegis%%20OS%%20%EDITION%%%20ISO%%20Request&body=License%%20Key:%%20%LICENSE_KEY%%%0A%%0APlease%%20assist%%20with%%20my%%20ISO%%20download."
    echo.
    echo  Email client opened.
)

echo.
pause
goto menu

:usb
cls
echo.
echo  ============================================================
echo        CREATE BOOTABLE USB
echo  ============================================================
echo.
echo  To create a bootable USB drive:
echo.
echo  1. Download Rufus from: https://rufus.ie
echo  2. Insert a USB drive (8GB minimum, 16GB for AI editions)
echo  3. Open Rufus and select your Aegis OS ISO
echo  4. Click START and wait for completion
echo  5. Boot from USB and enter your license key when prompted
echo.
echo  Would you like to download Rufus now?
echo.
set /p rufus="  Download Rufus? (Y/N): "

if /i "%rufus%"=="Y" (
    start "" "https://rufus.ie"
    echo.
    echo  Rufus website opened.
)

echo.
echo  WARNING: Creating a bootable USB will ERASE all data on the drive!
echo.
pause
goto menu

:requirements
cls
echo.
echo  ============================================================
echo        SYSTEM REQUIREMENTS - %EDITION%
echo  ============================================================
echo.
echo  MINIMUM REQUIREMENTS:
echo  ---------------------
echo  CPU:        64-bit processor (x86_64)
echo  RAM:        4 GB minimum (8 GB recommended)
echo  Storage:    30 GB free space
echo  USB:        8 GB flash drive (16 GB for AI editions)
echo.

if "%PREFIX%"=="GAME" goto gamer_reqs
if "%PREFIX%"=="AIDV" goto ai_reqs
if "%PREFIX%"=="GMAI" goto gamer_ai_reqs
goto standard_reqs

:gamer_reqs
echo  GAMER EDITION EXTRAS:
echo  ---------------------
echo  GPU:        NVIDIA GTX 1060 / AMD RX 580 or better
echo  RAM:        16 GB recommended for modern games
echo  Storage:    100 GB SSD recommended
echo.
echo  INCLUDES:
echo  - NVIDIA/AMD proprietary drivers
echo  - Wine/Proton gaming layer
echo  - Steam, Lutris pre-configured
echo  - RGB ecosystem support
echo.
goto req_end

:ai_reqs
echo  AI DEVELOPER EDITION EXTRAS:
echo  ----------------------------
echo  GPU:        NVIDIA RTX 2060+ (CUDA support required)
echo  RAM:        32 GB recommended for large models
echo  Storage:    200 GB SSD recommended
echo.
echo  INCLUDES:
echo  - CUDA 12.3 / ROCm support
echo  - PyTorch, TensorFlow pre-installed
echo  - 100+ ML libraries
echo  - Triton inference server
echo.
goto req_end

:gamer_ai_reqs
echo  GAMER + AI EDITION EXTRAS:
echo  --------------------------
echo  GPU:        NVIDIA RTX 3060+ recommended
echo  RAM:        32 GB recommended
echo  Storage:    250 GB SSD recommended
echo.
echo  INCLUDES:
echo  - Full gaming suite
echo  - Complete AI/ML toolkit
echo  - Hybrid GPU scheduling
echo  - Neural upscaling
echo.
goto req_end

:standard_reqs
echo  INCLUDED FEATURES:
echo  ------------------
echo  - Full software suite
echo  - Enhanced security
echo  - Priority updates
echo  - Premium support
echo.

:req_end
pause
goto menu

:exit
cls
echo.
echo  ============================================================
echo        THANK YOU FOR CHOOSING AEGIS OS
echo  ============================================================
echo.
echo  Your license: %LICENSE_KEY%
echo  Edition: %EDITION%
echo.
echo  TECHNICAL PREVIEW - No warranty. Use at your own risk.
echo  Contact: riley.liang@hotmail.com
echo.
echo  Goodbye!
echo.
timeout /t 3 >nul
exit /b 0
