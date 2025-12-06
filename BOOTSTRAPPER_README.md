# TurnIT Bootstrapper - Distribution Guide

## Overview

The TurnIT Bootstrapper is a standalone executable that automates the complete installation and setup of the TurnIT application for end users. It handles everything automatically, requiring zero technical knowledge from users.

## What the Bootstrapper Does

When a user runs `TurnIT-Setup.exe`, it automatically:

1. ✅ **Checks Python** - Detects if Python 3.10+ is installed
   - If missing: Downloads and installs Python automatically
   - Adds Python to Windows PATH
   - Verifies installation

2. ✅ **Checks Git** - Detects if Git is installed
   - If missing: Downloads and installs Git for Windows automatically
   - Adds Git to Windows PATH
   - Verifies installation

3. ✅ **Clones Repository** - Downloads the TurnIT project from GitHub
   - Default location: `C:\Users\<Username>\TurnIT`
   - User can choose a custom location
   - Skips if already cloned

4. ✅ **Installs Dependencies** - Installs all Python packages
   - Automatically reads from `requirements.txt`
   - Upgrades pip first
   - Shows installation progress

5. ✅ **Launches Application** - Starts TurnIT automatically
   - Runs `main_app.py`
   - On subsequent runs, skips installation steps and launches directly

## Building the Bootstrapper

### Quick Build

```powershell
cd C:\Users\setta\Desktop\code\TurnIT
.\build_bootstrapper.bat
```

The executable will be created at: `dist\TurnIT-Setup.exe`

### Manual Build

```powershell
pyinstaller --onefile --name="TurnIT-Setup" bootstrapper.py
```

See `BUILD_BOOTSTRAPPER.md` for advanced build options.

## File Structure

```
TurnIT/
├── bootstrapper.py              # Main bootstrapper script
├── build_bootstrapper.bat       # Automated build script
├── BUILD_BOOTSTRAPPER.md        # Detailed build instructions
├── BOOTSTRAPPER_README.md       # This file
└── dist/
    └── TurnIT-Setup.exe         # Compiled executable (after building)
```

## Distribution Workflow

### Step 1: Prepare Your GitHub Repository

Make sure your GitHub repository contains:
- `main_app.py` (main application entry point)
- `requirements.txt` (all Python dependencies)
- All application code and resources

### Step 2: Update Configuration

Edit `bootstrapper.py` and set your repository URL:

```python
GITHUB_REPO_URL = "https://github.com/putbullet/TurnIT.git"
```

### Step 3: Build the Bootstrapper

```powershell
.\build_bootstrapper.bat
```

This creates `dist\TurnIT-Setup.exe` (~10-15 MB)

### Step 4: Test the Bootstrapper

**Important**: Test on a clean machine or virtual machine that doesn't have Python/Git installed.

1. Copy `TurnIT-Setup.exe` to test machine
2. Double-click to run
3. Follow on-screen prompts
4. Verify it installs everything and launches TurnIT

### Step 5: Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `TurnIT v1.0.0`
5. Upload `TurnIT-Setup.exe` as a release asset
6. Write release notes

Example release notes:

```markdown
# TurnIT v1.0.0

## Installation

1. Download `TurnIT-Setup.exe`
2. Double-click to run
3. Follow on-screen instructions

The setup will automatically install Python, Git, and all dependencies.

## Features

- Voice to Text transcription
- Text to Speech synthesis
- Image Analysis with AI

## Requirements

- Windows 10 or higher
- Internet connection (for initial setup)
- ~500 MB free disk space

## What's New

- Initial release
- Automatic installation system
- Three main features: Voice to Text, Text to Speech, Image Analysis
```

### Step 6: Share with Users

Users simply:
1. Visit your GitHub releases page
2. Download `TurnIT-Setup.exe`
3. Run it
4. Done!

## User Instructions

Create a simple guide for users:

---

### How to Install TurnIT

1. **Download** the installer:
   - Go to: https://github.com/putbullet/TurnIT/releases/latest
   - Download `TurnIT-Setup.exe`

2. **Run** the installer:
   - Double-click `TurnIT-Setup.exe`
   - If Windows shows a security warning, click "More info" → "Run anyway"

3. **Follow** the setup wizard:
   - The installer will automatically:
     - Install Python (if needed)
     - Install Git (if needed)
     - Download TurnIT
     - Install all dependencies
     - Launch the application

4. **Wait** for completion:
   - First-time setup takes 5-10 minutes
   - You'll see progress messages
   - TurnIT will launch automatically when ready

5. **Enjoy**!
   - To run TurnIT again later, just double-click `TurnIT-Setup.exe`
   - It will skip installation and launch directly

---

## Technical Details

### Bootstrapper Features

- **Idempotent**: Can be run multiple times safely
- **Smart detection**: Skips already-installed components
- **Error handling**: Graceful error messages and recovery
- **Progress feedback**: Clear messages at every step
- **User prompts**: Asks for confirmation when needed
- **Automatic updates**: Pulls latest code on each run (if repository exists)

### Installation Locations

| Component | Default Location |
|-----------|------------------|
| Python | `C:\Users\<User>\AppData\Local\Programs\Python\Python3XX` |
| Git | `C:\Program Files\Git` |
| TurnIT Project | `C:\Users\<User>\TurnIT` |

Users can customize the project location during setup.

### Python Packages Installed

The bootstrapper installs packages from `requirements.txt`:
- PySide6 (Qt GUI framework)
- OpenAI Whisper (speech recognition)
- gTTS (text to speech)
- transformers (AI models)
- torch (machine learning)
- And all other dependencies

## Customization

### Change Repository URL

Edit `bootstrapper.py`:

```python
GITHUB_REPO_URL = "https://github.com/YourUsername/YourProject.git"
```

### Change Project Name

```python
PROJECT_NAME = "YourApp"
```

### Change Main Script

```python
MAIN_SCRIPT = "your_main_file.py"
```

### Change Python Version Requirement

```python
MIN_PYTHON_VERSION = (3, 10)  # Requires Python 3.10+
```

### Change Installation Directory

```python
DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser("~"), "CustomFolder", PROJECT_NAME)
```

## Troubleshooting

### Build Issues

**Problem**: "PyInstaller not found"
```powershell
pip install pyinstaller
```

**Problem**: "Module not found" during build
```powershell
pyinstaller --onefile --hidden-import=MODULE_NAME bootstrapper.py
```

### Runtime Issues

**Problem**: Users report "Missing Python DLL"
- Solution: Users should run `TurnIT-Setup.exe`, which installs Python correctly

**Problem**: "Git clone failed"
- Solution: Check internet connection and repository URL

**Problem**: "Permission denied" during installation
- Solution: Run as Administrator (right-click → "Run as administrator")

### Antivirus Warnings

Some antivirus programs may flag PyInstaller executables as suspicious. This is a false positive.

**Solutions**:
1. Add `--noupx` flag when building (disables compression)
2. Submit to antivirus vendors for whitelisting
3. Use code signing (requires certificate, costs money)

Build without compression:
```powershell
pyinstaller --onefile --noupx --name="TurnIT-Setup" bootstrapper.py
```

## Advantages of This Approach

✅ **One-click installation** - Users don't need to install Python/Git manually
✅ **Always up-to-date** - Pulls latest code from GitHub on each run
✅ **Small download** - Bootstrapper is only 10-15 MB
✅ **Automatic updates** - Repository can be updated without rebuilding bootstrapper
✅ **No Python required** - Installs Python automatically if missing
✅ **Cross-machine compatible** - Works on any Windows 10+ machine
✅ **User-friendly** - Clear messages and progress indicators
✅ **Error recovery** - Handles failures gracefully

## Comparison: Bootstrapper vs Full EXE

| Aspect | Bootstrapper | Full PyInstaller EXE |
|--------|--------------|----------------------|
| Download size | 10-15 MB | 500-1000 MB+ |
| Updates | Automatic from GitHub | Must rebuild and redistribute |
| Python dependency | Installs automatically | Bundled (outdated quickly) |
| Build time | 1-2 minutes | 10-30 minutes |
| Complexity | Simple | Complex with many dependencies |
| First run time | 5-10 minutes (download/install) | Immediate |
| Subsequent runs | Immediate | Immediate |

## Next Steps

1. ✅ Build the bootstrapper: `.\build_bootstrapper.bat`
2. ✅ Test on a clean machine
3. ✅ Upload to GitHub releases
4. ✅ Share download link with users
5. ✅ Update your GitHub README with installation instructions

## Support

If users encounter issues:
1. Check that they have internet connection
2. Try running as Administrator
3. Check antivirus isn't blocking the installer
4. Verify the GitHub repository URL is correct and accessible

## License

The bootstrapper is part of the TurnIT project and uses the same license.
