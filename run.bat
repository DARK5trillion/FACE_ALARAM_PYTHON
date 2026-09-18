@echo off
echo ==========================================
echo  Face Security Alarm System - Launcher
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
) else (
    echo Dependencies already installed.
)
echo.

echo Starting Face Security Alarm System...
echo.
python main.py

echo.
echo Program ended.
pause