@echo off
title Aegis OS USB Creator
color 1F

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo ============================================
    echo  Aegis OS USB Creator requires Administrator
    echo ============================================
    echo.
    echo Please right-click and "Run as Administrator"
    echo.
    pause
    exit /b
)

cls
echo.
echo ============================================
echo      Aegis OS USB Creator v3.0
echo      One-Click USB Installation
echo ============================================
echo.
echo This will create a bootable Aegis OS USB drive
echo.
echo Features:
echo  - Automatic USB detection
echo  - Freemium Edition (FREE)
echo  - XFCE Desktop Environment
echo  - Aegis DeskLink Basic (2 PCs)
echo  - No license required
echo.
echo WARNING: All data on the USB will be ERASED!
echo.
pause

:: Run the USB creator
python aegis-usb-creator.py

if %errorLevel% EQU 0 (
    echo.
    echo ============================================
    echo         USB Creation Complete!
    echo ============================================
    echo.
    echo Your Aegis OS USB is ready!
    echo.
    echo Next steps:
    echo  1. Safely eject the USB drive
    echo  2. Boot from USB (F12/F8 at startup)
    echo  3. Follow installation wizard
    echo.
) else (
    echo.
    echo ============================================
    echo         USB Creation Failed
    echo ============================================
    echo.
    echo Please ensure:
    echo  - USB drive is inserted
    echo  - Running as Administrator
    echo  - At least 8GB available
    echo.
)

pause