@echo off
REM Rocky Multi-Page Website Startup Script

echo 🚀 Rocky Multi-Page Website
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Install required packages
echo 📦 Installing dependencies...
pip install flask flask-cors -q

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed
echo.

REM Start the Flask app
echo 🎬 Starting Rocky Multi-Page Website...
echo 📍 Pages: Home, About, Contact
echo 📍 Open http://localhost:5000 in your browser
echo 🤖 Rocky is walking and ready to chat!
echo.

python web_app.py

pause

