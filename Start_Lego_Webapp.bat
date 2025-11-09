@echo off
title LEGO BrickLink Analysis - Web Server
color 0A

echo.
echo ========================================
echo    LEGO BrickLink Analysis System
echo ========================================
echo.
echo Starting web server...
echo.

cd /d "C:\Development\Lego_Bricklink"

REM Activate virtual environment
call "lego_env_313\Scripts\activate.bat"

REM Start Flask web app
python web_app.py

pause
