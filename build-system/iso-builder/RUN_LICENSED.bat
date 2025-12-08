@echo off
title Aegis OS ISO Builder - Licensed
echo Starting Aegis OS Licensed Builder...
echo.
python aegis_iso_builder.py --licensed
if errorlevel 1 (
    echo.
    echo Python not found! Please install Python from python.org
    echo.
    pause
)
