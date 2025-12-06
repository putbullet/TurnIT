# TurnIT - Quick Start Guide

## Welcome to TurnIT! 🎉

TurnIT is your AI-powered desktop assistant for voice, text, and image processing. This guide will help you get started in minutes.

## First Time Setup

1. **Launch TurnIT** - Double-click the TurnIT icon
2. **Accept Terms** - Check the box to agree to Terms & Privacy Policy
3. **Click "Start Here"** - The app will initialize
4. **AI Models Download** - First launch will download AI models (~2GB, one-time only)

## Main Features

### 🎤 Voice to Text

**Convert speech to text with AI**

1. Click "Voice to Text" from main menu
2. Select your microphone from dropdown
3. Choose language (English, Arabic, French, etc.)
4. Click "Confirm Configuration"
5. Click "Start Recording" 🔴
6. Speak clearly into your microphone
7. Watch the live audio level indicator (green circle)
8. Click "Stop Recording" ⏹️
9. Wait for AI transcription (few seconds)
10. Export transcription with "Export to TXT"

**Tips:**
- Use a good microphone for best results
- Speak clearly at normal pace
- Minimize background noise
- Green audio indicator shows input level

### 🗣️ Text to Voice

**Convert text to natural speech**

1. Click "Text to Voice" from main menu
2. Type or paste your text (up to 5000 characters)
3. Select voice from dropdown
4. Adjust speech rate (0.5x - 2.0x)
5. Click "Synthesize Speech"
6. Wait for generation (few seconds)
7. Click ▶️ Play to listen
8. Click "Save Audio File" to export

**Tips:**
- Different voices for different styles
- Slower rate for presentations
- Faster rate for quick reviews
- Supports multiple languages

### 🖼️ Image Analysis

**Extract information from images with AI**

1. Click "Images Analysis" from main menu
2. Click "Load Image" to select file
3. Click "Analyze Image" to start AI processing
4. View different analysis tabs:
   - **AI Features**: Deep learning analysis
   - **OCR**: Extracted text from image
   - **Colors**: Color palette analysis
5. Click "Export to JSON" to save results

**Supported Formats:**
- JPG, JPEG, PNG, BMP, TIFF, WEBP

**Tips:**
- Higher resolution images give better results
- OCR works best with clear, high-contrast text
- First analysis may take longer (model loading)

## Settings ⚙️

Click the gear icon in top-right corner to configure:

- **Language**: Switch UI language (English/Arabic/French)
- **Theme**: Dark theme (default)
- **Audio Settings**: Test microphone and speakers
- **About**: View version and credits

## Keyboard Shortcuts

- **Ctrl+Q** - Quit application
- **Ctrl+S** - Save current work
- **Esc** - Close current window
- **F11** - Toggle fullscreen (where available)

## Common Issues & Solutions

### Audio Recording Not Working
1. Check microphone is connected
2. Select correct device in dropdown
3. Check Windows audio permissions
4. Try different USB port (if USB mic)

### Transcription Accuracy Issues
1. Ensure clear audio with minimal noise
2. Select correct language
3. Speak clearly and at normal pace
4. Check microphone quality

### AI Models Not Downloading
1. Check internet connection
2. Ensure 2GB+ free disk space
3. Check firewall/antivirus settings
4. Wait patiently (can take 10-30 minutes)

### Application Crashes
1. Check logs in `TurnIT/logs/` folder
2. Ensure 4GB+ RAM available
3. Close other heavy applications
4. Restart TurnIT

### Out of Memory Errors
1. Close other applications
2. Restart TurnIT
3. Increase system virtual memory
4. Consider upgrading RAM

## Performance Tips

- **First Launch**: Be patient, model download is one-time
- **RAM**: Close unnecessary applications
- **Storage**: Keep 5GB+ free space
- **CPU**: Background AI processing is CPU-intensive
- **SSD**: Faster model loading vs HDD

## Privacy & Security

✅ **All processing happens locally on your computer**
✅ **No data is sent to any servers**
✅ **No internet required after setup**
✅ **Your files stay on your device**
✅ **No tracking or telemetry**

## File Locations

- **Application**: `C:\Program Files\TurnIT\` (or installation folder)
- **Logs**: `TurnIT/logs/`
- **Models**: `TurnIT/models/` (~2GB)
- **Config**: `TurnIT/config/settings.json`
- **Exports**: Your chosen save location

## System Requirements

**Minimum:**
- Windows 10/11 64-bit
- 4 GB RAM
- 2 GB free space
- Dual-core CPU

**Recommended:**
- 8 GB+ RAM
- 5 GB free space
- Quad-core CPU
- SSD drive

## Getting Help

- **Documentation**: See README.md
- **Issues**: Report bugs on GitHub
- **Email**: support@turnit.ai
- **Logs**: Check `logs/` folder for error details

## Updates

TurnIT will notify you when updates are available. You can:
- Download new version from website
- Check current version in Settings → About

## Uninstalling

To completely remove TurnIT:
1. Uninstall via Windows Settings → Apps
2. Delete remaining files:
   - `C:\Program Files\TurnIT\` (or install location)
   - `%APPDATA%\TurnIT\`
   - `%LOCALAPPDATA%\TurnIT\`

---

**Need More Help?**

- Full documentation: README.md
- Report issues: GitHub Issues
- Contact: support@turnit.ai

**Made with ❤️ by putbullet**

Version 1.0.0 | December 2024
