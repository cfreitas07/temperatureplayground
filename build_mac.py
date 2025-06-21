#!/usr/bin/env python3
"""
Build script for creating macOS executable of Temperature Playground
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    print("=== Temperature Playground - macOS Build Script ===")
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("❌ This script is designed for macOS only!")
        print("For Windows, use: pyinstaller --onefile --windowed serial_terminal.py")
        print("For Linux, use: pyinstaller --onefile serial_terminal.py")
        return False
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")
    
    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create the executable
    print("\n🔨 Building macOS app...")
    
    # PyInstaller command for macOS
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name=TemperaturePlayground", # App name
        "--icon=app_icon.icns",         # App icon (if available)
        "--add-data=requirements.txt:.", # Include requirements
        "--hidden-import=matplotlib.backends.backend_qt5agg",
        "--hidden-import=scipy.interpolate",
        "--hidden-import=numpy",
        "--hidden-import=serial",
        "--hidden-import=serial.tools.list_ports",
        "--collect-all=matplotlib",
        "--collect-all=scipy",
        "serial_terminal.py"
    ]
    
    if not run_command(" ".join(pyinstaller_cmd), "Creating executable"):
        return False
    
    # Check if build was successful
    app_path = "dist/TemperaturePlayground"
    if os.path.exists(app_path):
        print(f"\n✅ Success! Executable created at: {app_path}")
        print(f"📁 Size: {os.path.getsize(app_path) / (1024*1024):.1f} MB")
        
        # Make it executable
        run_command(f"chmod +x {app_path}", "Making executable")
        
        print("\n🎉 Build completed successfully!")
        print("\nTo run the app:")
        print(f"  ./{app_path}")
        print("\nTo distribute:")
        print("  1. Copy the executable to your Mac")
        print("  2. Right-click and select 'Open' (first time)")
        print("  3. The app will be available in Applications")
        
        return True
    else:
        print("❌ Build failed - executable not found!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 