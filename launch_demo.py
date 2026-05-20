#!/usr/bin/env python3
"""
Rocky Demo Website - One-Click Launcher
Installs dependencies and starts the server
"""

import subprocess
import sys
import os
import platform
import webbrowser
import time

def run_command(cmd):
    """Run shell command and return success status"""
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("\n" + "="*50)
    print("  🚀  ROCKY DEMO WEBSITE LAUNCHER  🚀")
    print("="*50 + "\n")
    
    # Check Python
    print("✓ Python version:", sys.version.split()[0])
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if run_command(f"{sys.executable} -m pip install -q flask flask-cors"):
        print("✓ Dependencies installed")
    else:
        print("⚠ Warning: Could not install packages (you may need to run manually)")
    
    # Change to correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Start Flask
    print("\n🎬 Starting Rocky Demo Website...")
    print("📍 URL: http://localhost:5000")
    print("⏱  Server starting in 2 seconds...")
    print("\n" + "="*50)
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    time.sleep(2)
    
    # Try to open browser automatically
    try:
        webbrowser.open("http://localhost:5000")
        print("✓ Browser opened automatically\n")
    except:
        print("⚠ Please open http://localhost:5000 in your browser\n")
    
    # Start Flask
    os.system(f"{sys.executable} web_app.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped. Goodbye! 👋")
        sys.exit(0)
