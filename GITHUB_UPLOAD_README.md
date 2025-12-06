# Uploading TurnIT to GitHub - Complete Guide

## Overview

This guide walks you through uploading your TurnIT project to GitHub and setting up automatic distribution using the bootstrapper system.

## What You'll Accomplish

✅ Upload your complete TurnIT project to GitHub  
✅ Users can download a tiny executable (~15 MB)  
✅ Executable automatically installs Python, Git, and all dependencies  
✅ Users get the full TurnIT application with zero technical knowledge required  
✅ Updates are automatic - just push to GitHub, users run the bootstrapper again  

---

## Step 1: Prepare Your Repository

### 1.1 Update the Repository URL

Edit `bootstrapper.py` and update line 26:

```python
GITHUB_REPO_URL = "https://github.com/putbullet/TurnIT.git"  # Change to your repo URL
```

Replace `putbullet/TurnIT` with your actual GitHub username and repository name.

### 1.2 Create .gitignore

Create a `.gitignore` file in your TurnIT folder to exclude unnecessary files:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# PyInstaller
*.spec
build/
dist/

# Cache
cache/
*.cache

# Logs
logs/
*.log

# Models (optional - include if models are small, exclude if large)
models/
*.pth
*.bin
*.onnx

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary files
temp_*.mp3
temp_*.wav
*.tmp

# Database
*.db
*.sqlite3
```

### 1.3 Verify Essential Files

Make sure these files exist in your TurnIT folder:

- ✅ `main_app.py` - Main application entry point
- ✅ `requirements.txt` - All Python dependencies
- ✅ `README.md` - Project description
- ✅ `LICENSE.txt` - Your license
- ✅ `bootstrapper.py` - The bootstrapper script
- ✅ `build_bootstrapper.bat` - Bootstrapper build script
- ✅ All your code files (`ui/`, `utils/`, `ai/`, `config/`)

---

## Step 2: Build the Bootstrapper

### 2.1 Build the Executable

Open PowerShell in your TurnIT folder and run:

```powershell
.\build_bootstrapper.bat
```

This creates `dist\TurnIT-Setup.exe` (~10-15 MB).

### 2.2 Test the Bootstrapper

**Critical**: Test on a machine without Python/Git installed.

If you don't have a clean machine, create a Windows VM or ask a friend to test.

1. Copy `dist\TurnIT-Setup.exe` to test machine
2. Double-click to run
3. Verify it:
   - Installs Python (if missing)
   - Installs Git (if missing)
   - Clones your repository
   - Installs dependencies
   - Launches TurnIT

---

## Step 3: Upload to GitHub

### 3.1 Initialize Git Repository

Open PowerShell in your TurnIT folder:

```powershell
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - TurnIT v1.0.0"
```

### 3.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `TurnIT`
3. Description: "AI-powered application with Voice to Text, Text to Speech, and Image Analysis"
4. Choose: Public (recommended) or Private
5. **Don't** initialize with README, .gitignore, or license (you already have these)
6. Click "Create repository"

### 3.3 Push to GitHub

GitHub will show you commands. Use these:

```powershell
# Add remote
git remote add origin https://github.com/putbullet/TurnIT.git

# Set branch name
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note**: Replace `putbullet/TurnIT` with your actual username/repository.

### 3.4 Verify Upload

1. Go to your repository: `https://github.com/putbullet/TurnIT`
2. Verify all files are there
3. Check that `main_app.py` and `requirements.txt` are present

---

## Step 4: Create a GitHub Release

### 4.1 Create a New Release

1. Go to your repository: `https://github.com/putbullet/TurnIT`
2. Click "Releases" (right sidebar)
3. Click "Create a new release"

### 4.2 Fill Release Information

**Choose a tag**: `v1.0.0`  
**Release title**: `TurnIT v1.0.0 - Initial Release`  
**Description**:

```markdown
# TurnIT v1.0.0

AI-powered desktop application with three main features:
- 🎤 **Voice to Text**: Transcribe audio using OpenAI Whisper
- 🔊 **Text to Speech**: Convert text to natural speech
- 🖼️ **Image Analysis**: AI-powered image recognition and description

## Installation

### For Users (Non-Technical)

1. Download `TurnIT-Setup.exe` below
2. Double-click to run
3. Follow on-screen instructions

The installer automatically handles:
- ✅ Python installation (if needed)
- ✅ Git installation (if needed)
- ✅ Project download
- ✅ Dependency installation
- ✅ Application launch

**First-time setup**: 5-10 minutes  
**Subsequent runs**: Instant launch

### System Requirements

- Windows 10 or higher
- Internet connection (for initial setup)
- ~500 MB free disk space
- Microphone (for Voice to Text)
- Speakers (for Text to Speech)

## Features

### Voice to Text
- High-quality speech recognition using OpenAI Whisper
- Support for multiple languages
- Real-time audio level monitoring
- Save transcriptions to file

### Text to Speech
- Natural-sounding voice synthesis
- Multiple language support
- Adjustable speech rate
- Export audio files

### Image Analysis
- AI-powered image description
- Object detection
- Text extraction (OCR)
- Support for multiple image formats

## What's New in v1.0.0

- Initial release
- Three main features fully implemented
- Modern Qt6-based user interface
- Automatic installation system
- Multi-language support (English/French)

## Technical Details

- **Python**: 3.10+
- **GUI Framework**: PySide6 (Qt6)
- **AI Models**: OpenAI Whisper, Transformers, EasyOCR
- **Speech Synthesis**: gTTS, pyttsx3
- **Audio Processing**: sounddevice, librosa

## License

MIT License - See LICENSE.txt for details

## Support

Issues? Questions? Open an issue on GitHub:
https://github.com/putbullet/TurnIT/issues
```

### 4.3 Upload the Bootstrapper

1. In the "Attach binaries" section
2. Drag and drop `dist\TurnIT-Setup.exe`
3. Wait for upload to complete

### 4.4 Publish Release

Click "Publish release"

Your release is now live at: `https://github.com/putbullet/TurnIT/releases/tag/v1.0.0`

---

## Step 5: Update Your README

Update your `README.md` to include download instructions:

```markdown
# TurnIT

AI-powered desktop application for Windows with Voice to Text, Text to Speech, and Image Analysis.

## Quick Start

### Download & Install

1. Go to [Releases](https://github.com/putbullet/TurnIT/releases/latest)
2. Download `TurnIT-Setup.exe`
3. Run the executable
4. Follow on-screen instructions

That's it! The installer handles everything automatically.

## Features

### 🎤 Voice to Text
Transcribe audio using state-of-the-art AI (OpenAI Whisper)

### 🔊 Text to Speech
Convert text to natural-sounding speech

### 🖼️ Image Analysis
AI-powered image description and analysis

## Requirements

- Windows 10 or higher
- Internet connection (for initial setup)
- ~500 MB free disk space

## How It Works

The installer automatically:
1. Checks for Python 3.10+ (installs if missing)
2. Checks for Git (installs if missing)
3. Downloads TurnIT from GitHub
4. Installs all dependencies
5. Launches the application

On subsequent runs, it skips installation and launches directly.

## For Developers

### Manual Installation

```bash
git clone https://github.com/putbullet/TurnIT.git
cd TurnIT
pip install -r requirements.txt
python main_app.py
```

### Building the Bootstrapper

```bash
.\build_bootstrapper.bat
```

See `BUILD_BOOTSTRAPPER.md` for details.

## License

MIT License - see LICENSE.txt

## Screenshots

[Add screenshots here]
```

Commit and push the updated README:

```powershell
git add README.md
git commit -m "Updated README with download instructions"
git push
```

---

## Step 6: Share with Users

### 6.1 Direct Download Link

Share this link with users:

```
https://github.com/putbullet/TurnIT/releases/latest/download/TurnIT-Setup.exe
```

This always downloads the latest version.

### 6.2 User Instructions

Provide users with these simple steps:

---

**How to Install TurnIT**

1. Download: [TurnIT-Setup.exe](https://github.com/putbullet/TurnIT/releases/latest/download/TurnIT-Setup.exe)
2. Run the downloaded file
3. If Windows shows a security warning:
   - Click "More info"
   - Click "Run anyway"
4. Follow the on-screen instructions
5. Wait for setup to complete (5-10 minutes first time)
6. TurnIT will launch automatically!

To run TurnIT again later, just double-click `TurnIT-Setup.exe`.

---

## Step 7: Updating Your Application

### 7.1 Make Changes

Edit your code as needed in the TurnIT folder.

### 7.2 Commit and Push

```powershell
git add .
git commit -m "Description of changes"
git push
```

### 7.3 That's It!

Users don't need to download anything new. When they run `TurnIT-Setup.exe`, it automatically:
1. Pulls the latest code from GitHub
2. Installs any new dependencies
3. Launches the updated application

### 7.4 Creating a New Release (Optional)

For major updates, create a new release:

1. Update version in your code
2. Commit and push changes
3. Go to GitHub → Releases → "Draft a new release"
4. New tag: `v1.1.0`
5. Describe what's new
6. Optionally rebuild and upload a new `TurnIT-Setup.exe` (not required if only code changed)

---

## Troubleshooting

### Users Report Download Issues

**Problem**: Antivirus blocking the download

**Solution**: Users should:
1. Check antivirus/Windows Defender
2. Add exception for `TurnIT-Setup.exe`
3. Alternatively, download from GitHub releases page directly

### Users Report Installation Failures

**Problem**: Python/Git installation fails

**Solution**: Users should:
1. Run as Administrator (right-click → "Run as administrator")
2. Check internet connection
3. Manually install Python from python.org if automatic install fails

### Repository Clone Fails

**Problem**: "Git clone failed" error

**Solutions**:
1. Verify repository is public (or user has access if private)
2. Check repository URL in `bootstrapper.py` is correct
3. User should check internet connection

### Dependencies Installation Fails

**Problem**: pip install errors

**Solutions**:
1. User should ensure internet connection is stable
2. Run as Administrator
3. Some packages (like torch) are large and may take time

---

## Advanced Topics

### Using Private Repository

If your repository is private:

1. Users need GitHub authentication
2. Alternative: Include a personal access token (not recommended for security)
3. Better: Keep repository public or use a different distribution method

### Code Signing

To avoid antivirus warnings:

1. Purchase a code signing certificate (~$100-300/year)
2. Sign the executable:

```powershell
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com TurnIT-Setup.exe
```

This eliminates most antivirus false positives.

### Customizing Install Location

Users can choose installation directory by editing `bootstrapper.py`:

```python
DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser("~"), "MyCustomFolder", PROJECT_NAME)
```

Rebuild the bootstrapper after changes.

---

## Checklist

Before distributing:

- [ ] `bootstrapper.py` has correct GitHub URL
- [ ] `.gitignore` excludes unnecessary files
- [ ] `requirements.txt` is complete and accurate
- [ ] `README.md` has clear instructions
- [ ] Bootstrapper tested on clean machine
- [ ] All code committed to GitHub
- [ ] GitHub release created
- [ ] `TurnIT-Setup.exe` uploaded to release
- [ ] Download link tested
- [ ] User instructions provided

---

## Summary

### What Users Download
- One small file: `TurnIT-Setup.exe` (~15 MB)

### What Happens Automatically
1. Python installation (if needed)
2. Git installation (if needed)
3. Repository clone from GitHub
4. Dependency installation
5. Application launch

### Benefits
- ✅ Zero technical knowledge required
- ✅ Always up-to-date (pulls from GitHub)
- ✅ Small download size
- ✅ Automatic updates
- ✅ Cross-machine compatibility
- ✅ No manual Python/Git setup

### For You (Developer)
- ✅ Easy to update (just git push)
- ✅ No need to rebuild large executables
- ✅ Users always get latest code
- ✅ Simple distribution workflow

---

## Next Steps

1. Follow this guide step-by-step
2. Upload your project to GitHub
3. Build and upload the bootstrapper
4. Share the download link
5. Enjoy automatic distribution!

## Questions?

Open an issue on your repository or contact the development team.

---

**Good luck with your TurnIT distribution! 🚀**
