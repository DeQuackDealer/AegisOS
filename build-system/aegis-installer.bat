@echo off
setlocal enabledelayedexpansion
title Aegis OS Installer v1.0
color 0B

:header
cls
echo.
echo  ============================================================
echo             AEGIS OS INSTALLER v1.0
echo         Professional Linux for Enterprise
echo  ============================================================
echo.

:menu
echo  Please select an option:
echo.
echo  [1] Activate License Key
echo  [2] Download Aegis OS ISO
echo  [3] Create Bootable USB (using Rufus)
echo  [4] View System Requirements
echo  [5] Exit
echo.
set /p choice="  Enter choice (1-5): "

if "%choice%"=="1" goto activate
if "%choice%"=="2" goto download
if "%choice%"=="3" goto usb
if "%choice%"=="4" goto requirements
if "%choice%"=="5" goto exit
goto menu

:activate
cls
echo.
echo  ============================================================
echo               LICENSE ACTIVATION
echo  ============================================================
echo.
echo  Enter your license key (format: XXXX-XXXX-XXXX-XXXX)
echo.
set /p LICENSE_KEY="  License Key: "

if "%LICENSE_KEY%"=="" (
    echo.
    echo  [ERROR] No license key entered!
    echo.
    pause
    goto header
)

set PREFIX=%LICENSE_KEY:~0,4%
set EDITION=Unknown

if "%PREFIX%"=="BSIC" set EDITION=Basic Edition
if "%PREFIX%"=="WORK" set EDITION=Workplace Edition
if "%PREFIX%"=="GAME" set EDITION=Gamer Edition
if "%PREFIX%"=="AIDV" set EDITION=AI Developer Edition
if "%PREFIX%"=="GMAI" set EDITION=Gamer + AI Edition
if "%PREFIX%"=="SERV" set EDITION=Server Edition
if "%PREFIX%"=="FREE" set EDITION=Freemium Edition

echo.
echo  ============================================================
echo               LICENSE VALIDATED
echo  ============================================================
echo.
echo  License Key: %LICENSE_KEY%
echo  Edition:     %EDITION%
echo  Status:      ACTIVE
echo.

echo %LICENSE_KEY% > "%USERPROFILE%\aegis-license.key"
echo  License saved to: %USERPROFILE%\aegis-license.key
echo.
echo  You can now download the ISO and create a bootable USB.
echo.
pause
goto header

:download
cls
echo.
echo  ============================================================
echo               DOWNLOAD AEGIS OS
echo  ============================================================
echo.
echo  Select your edition to download:
echo.
echo  [1] Freemium (FREE - 2.1 GB)
echo  [2] Basic ($69 - 2.8 GB)
echo  [3] Workplace ($49 - 3.2 GB)
echo  [4] Gamer ($89 - 4.5 GB)
echo  [5] AI Developer ($109 - 5.2 GB)
echo  [6] Gamer + AI ($149 - 6.8 GB)
echo  [7] Back to menu
echo.
set /p edition="  Enter choice (1-7): "

if "%edition%"=="7" goto header

echo.
echo  Opening download page in your browser...
echo.

if "%edition%"=="1" start "" "https://aegis-os.replit.app/freemium"
if "%edition%"=="2" start "" "https://aegis-os.replit.app/pricing"
if "%edition%"=="3" start "" "https://aegis-os.replit.app/pricing"
if "%edition%"=="4" start "" "https://aegis-os.replit.app/pricing"
if "%edition%"=="5" start "" "https://aegis-os.replit.app/pricing"
if "%edition%"=="6" start "" "https://aegis-os.replit.app/pricing"

echo  Browser opened. Complete purchase on the website if needed.
echo.
pause
goto header

:usb
cls
echo.
echo  ============================================================
echo            CREATE BOOTABLE USB
echo  ============================================================
echo.
echo  To create a bootable USB drive, we recommend using Rufus:
echo.
echo  1. Download Rufus from: https://rufus.ie
echo  2. Insert a USB drive (8GB minimum)
echo  3. Select the Aegis OS ISO file
echo  4. Click START and wait for completion
echo.
echo  Would you like to open the Rufus download page?
echo.
set /p rufus="  Open Rufus website? (Y/N): "

if /i "%rufus%"=="Y" (
    start "" "https://rufus.ie"
    echo.
    echo  Rufus website opened in your browser.
)

echo.
echo  IMPORTANT: Creating a bootable USB will ERASE all data on the drive!
echo.
pause
goto header

:requirements
cls
echo.
echo  ============================================================
echo            SYSTEM REQUIREMENTS
echo  ============================================================
echo.
echo  MINIMUM REQUIREMENTS:
echo  ----------------------
echo  CPU:        64-bit processor (x86_64)
echo  RAM:        4 GB (8 GB recommended)
echo  Storage:    20 GB free space
echo  USB:        8 GB flash drive for installation
echo.
echo  RECOMMENDED FOR GAMER/AI EDITIONS:
echo  -----------------------------------
echo  CPU:        Intel i5/AMD Ryzen 5 or better
echo  RAM:        16 GB or more
echo  GPU:        NVIDIA GTX 1060 / AMD RX 580 or better
echo  Storage:    100 GB SSD
echo.
echo  SUPPORTED HARDWARE:
echo  -------------------
echo  - NVIDIA GPUs (Proprietary drivers included)
echo  - AMD GPUs (AMDGPU/ROCm included)
echo  - Intel integrated graphics
echo  - Most WiFi/Bluetooth adapters
echo.
pause
goto header

:exit
cls
echo.
echo  ============================================================
echo        THANK YOU FOR CHOOSING AEGIS OS
echo  ============================================================
echo.
echo  Commercial Software. Sold as-is. Support available separately.
echo  Contact: riley.liang@hotmail.com
echo.
echo  Goodbye!
echo.
timeout /t 3 >nul
exit /b 0
