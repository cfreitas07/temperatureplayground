# Temperature Playground - macOS Build Guide

This guide will help you create a standalone macOS executable of the Temperature Playground application.

## Prerequisites

### 1. Install Python 3.8+ on macOS
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
# https://www.python.org/downloads/macos/
```

### 2. Install Xcode Command Line Tools
```bash
xcode-select --install
```

### 3. Verify Python Installation
```bash
python3 --version
pip3 --version
```

## Building the Executable

### Option 1: Using the Build Script (Recommended)

1. **Clone or download the project files**
   ```bash
   cd /path/to/your/project
   ```

2. **Make the build script executable**
   ```bash
   chmod +x build_mac.py
   ```

3. **Run the build script**
   ```bash
   python3 build_mac.py
   ```

The script will:
- Install all required dependencies
- Clean previous builds
- Create a standalone executable
- Provide instructions for distribution

### Option 2: Manual Build

1. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Create the executable**
   ```bash
   pyinstaller --onefile --windowed --name=TemperaturePlayground serial_terminal.py
   ```

3. **Make it executable**
   ```bash
   chmod +x dist/TemperaturePlayground
   ```

## Distribution

### For Personal Use
- The executable will be created in the `dist/` folder
- Copy `dist/TemperaturePlayground` to your Mac
- Double-click to run (first time, right-click → Open)

### For Distribution to Others
1. **Create a DMG file (optional)**
   ```bash
   # Install create-dmg if you want to create a DMG
   brew install create-dmg
   
   # Create DMG
   create-dmg \
     --volname "Temperature Playground" \
     --window-pos 200 120 \
     --window-size 600 300 \
     --icon-size 100 \
     --icon "TemperaturePlayground.app" 175 120 \
     --hide-extension "TemperaturePlayground.app" \
     --app-drop-link 425 120 \
     "TemperaturePlayground.dmg" \
     "dist/"
   ```

2. **Share the executable or DMG file**

## Troubleshooting

### Common Issues

1. **"Permission denied" error**
   ```bash
   chmod +x dist/TemperaturePlayground
   ```

2. **"App is damaged" message**
   - Right-click the app → Open
   - Or run: `xattr -cr /path/to/TemperaturePlayground`

3. **Missing dependencies**
   ```bash
   pip3 install --upgrade pip
   pip3 install -r requirements.txt
   ```

4. **PyInstaller not found**
   ```bash
   pip3 install pyinstaller
   ```

5. **Matplotlib backend issues**
   - The build script includes the necessary hidden imports
   - If issues persist, try: `pip3 install --upgrade matplotlib`

### File Size
- The executable will be large (50-100MB) because it includes Python and all dependencies
- This is normal for PyInstaller applications

### Performance
- First launch may be slower as the app extracts resources
- Subsequent launches will be faster

## System Requirements

- **macOS**: 10.14 (Mojave) or later
- **Architecture**: Intel (x86_64) or Apple Silicon (arm64)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 200MB free space

## Security Notes

- macOS may show security warnings for unsigned apps
- To allow the app to run:
  1. Go to System Preferences → Security & Privacy
  2. Click "Open Anyway" for the app
  3. Or right-click the app → Open

## Alternative: Create a .app Bundle

For a more native macOS experience, you can create a proper .app bundle:

```bash
pyinstaller --onefile --windowed --name=TemperaturePlayground --icon=app_icon.icns serial_terminal.py
```

This creates `dist/TemperaturePlayground.app` which can be:
- Dragged to Applications folder
- Launched from Spotlight
- Added to Dock

## Support

If you encounter issues:
1. Check the console output for error messages
2. Ensure all dependencies are installed
3. Try running the Python script directly first: `python3 serial_terminal.py`
4. Check macOS security settings

## Files Created

After successful build:
- `dist/TemperaturePlayground` - The executable
- `build/` - Build artifacts (can be deleted)
- `TemperaturePlayground.spec` - PyInstaller spec file (can be kept for future builds) 