# Building the TurnIT Bootstrapper

This guide explains how to compile the bootstrapper script into a standalone executable.

## Overview

The bootstrapper (`bootstrapper.py`) is a Python script that automatically:
1. Checks for Python installation (installs if missing)
2. Checks for Git installation (installs if missing)
3. Clones the TurnIT repository from GitHub
4. Installs all dependencies
5. Launches the TurnIT application

## Prerequisites

Before building the bootstrapper, you need:
- Python 3.10 or higher installed
- PyInstaller package

## Step 1: Install PyInstaller

```powershell
pip install pyinstaller
```

## Step 2: Compile to Executable

### Option A: Basic Compilation (Console Window)

This creates an executable that shows a console window:

```powershell
pyinstaller --onefile --name="TurnIT-Setup" bootstrapper.py
```

### Option B: No Console Window (Silent Mode)

This creates an executable without a console window:

```powershell
pyinstaller --onefile --noconsole --name="TurnIT-Setup" bootstrapper.py
```

**Note**: The `--noconsole` option is NOT recommended for the bootstrapper because users won't see installation progress.

### Option C: With Custom Icon (Recommended)

If you have an icon file (`.ico` format):

```powershell
pyinstaller --onefile --name="TurnIT-Setup" --icon="path\to\icon.ico" bootstrapper.py
```

### Option D: Full Production Build (Best)

Complete build with all options:

```powershell
pyinstaller --onefile ^
    --name="TurnIT-Setup" ^
    --icon="path\to\icon.ico" ^
    --add-data="README.md;." ^
    --clean ^
    --noconfirm ^
    bootstrapper.py
```

## Step 3: Locate the Executable

After compilation, the executable will be in:
```
dist\TurnIT-Setup.exe
```

## Step 4: Test the Executable

1. Copy `TurnIT-Setup.exe` to a clean test directory
2. Double-click to run it
3. Follow the on-screen instructions
4. Verify it installs Python, Git, clones the repo, and launches TurnIT

## Distribution

Once tested, you can distribute `TurnIT-Setup.exe` to users. They simply:
1. Download `TurnIT-Setup.exe`
2. Double-click to run
3. Follow on-screen instructions

The bootstrapper handles everything automatically.

## Customization

Before building, you can customize the bootstrapper by editing these variables in `bootstrapper.py`:

```python
GITHUB_REPO_URL = "https://github.com/putbullet/TurnIT.git"  # Your repo URL
PROJECT_NAME = "TurnIT"
MAIN_SCRIPT = "main_app.py"  # Main Python file
REQUIREMENTS_FILE = "requirements.txt"
MIN_PYTHON_VERSION = (3, 10)  # Minimum Python version
DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser("~"), PROJECT_NAME)
```

## Advanced PyInstaller Options

### Reduce File Size

Add these options to reduce the executable size:

```powershell
pyinstaller --onefile ^
    --name="TurnIT-Setup" ^
    --exclude-module=tkinter ^
    --exclude-module=matplotlib ^
    bootstrapper.py
```

### Add Version Information (Windows)

Create a `version_info.txt` file:

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'TurnIT Development Team'),
        StringStruct(u'FileDescription', u'TurnIT Application Setup'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'TurnIT-Setup'),
        StringStruct(u'LegalCopyright', u'Copyright © 2025'),
        StringStruct(u'OriginalFilename', u'TurnIT-Setup.exe'),
        StringStruct(u'ProductName', u'TurnIT'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

Then build with:

```powershell
pyinstaller --onefile ^
    --name="TurnIT-Setup" ^
    --version-file="version_info.txt" ^
    bootstrapper.py
```

## Troubleshooting

### "Module not found" errors

If PyInstaller misses some modules, add them explicitly:

```powershell
pyinstaller --onefile ^
    --name="TurnIT-Setup" ^
    --hidden-import=urllib.request ^
    --hidden-import=winreg ^
    bootstrapper.py
```

### Antivirus False Positives

Some antivirus software may flag PyInstaller executables. To minimize this:
1. Use code signing (requires a code signing certificate)
2. Submit to antivirus vendors for whitelisting
3. Build with `--noupx` option (disables compression)

```powershell
pyinstaller --onefile --noupx --name="TurnIT-Setup" bootstrapper.py
```

### Large Executable Size

The bootstrapper executable is small (~10-15 MB) because it only includes:
- Python standard library modules used by the script
- No heavy dependencies like PyQt, NumPy, etc.

The actual TurnIT dependencies are downloaded and installed when the bootstrapper runs.

## Complete Build Script

Save this as `build_bootstrapper.bat`:

```batch
@echo off
echo ================================================
echo Building TurnIT Bootstrapper
echo ================================================

echo.
echo Step 1: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist TurnIT-Setup.spec del TurnIT-Setup.spec

echo.
echo Step 2: Building executable...
pyinstaller --onefile ^
    --name="TurnIT-Setup" ^
    --clean ^
    --noconfirm ^
    bootstrapper.py

echo.
echo ================================================
echo Build Complete!
echo ================================================
echo Executable location: dist\TurnIT-Setup.exe
echo.
pause
```

Run with:
```powershell
.\build_bootstrapper.bat
```

## Next Steps

After building the bootstrapper:

1. **Test thoroughly** on a clean Windows machine
2. **Upload to GitHub** in your releases
3. **Create a release** with clear instructions
4. **Share the download link** with users

Users will download only `TurnIT-Setup.exe` (~10-15 MB), and it will handle everything else automatically!
