#!/bin/bash
# Face Security Alarm System - Launcher for Linux/macOS

echo "=========================================="
echo "  Face Security Alarm System - Launcher"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.7+ from https://python.org or your package manager"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python found:"
$PYTHON_CMD --version
echo

# Check if requirements are installed
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import cv2" &> /dev/null; then
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully!"
else
    echo "Dependencies already installed."
fi
echo

echo "Starting Face Security Alarm System..."
echo
$PYTHON_CMD main.py

echo
echo "Program ended."