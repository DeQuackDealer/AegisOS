@echo off
title Aegis OS ISO Builder - Freemium
echo Starting Aegis OS Freemium Builder...
echo.
python aegis_iso_builder.py
if errorlevel 1 (
    echo.
    echo Python not found! Please install Python from python.org
    echo.
    pause
)
