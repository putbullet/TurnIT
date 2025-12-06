# TurnIT - AI Desktop Assistant

<div align="center">

**AI-Powered Desktop Tools for Your Daily Tasks**

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/putbullet/TurnIT)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.txt)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

</div>

## 🌟 Features

### 🎤 Voice to Text
Convert speech to text with state-of-the-art AI transcription using OpenAI Whisper:
- Real-time audio recording with live level monitoring
- Multiple language support (50+ languages)
- High accuracy transcription with Whisper-small model
- Export results to TXT files
- **Auto-installs missing dependencies on first use**

### 🗣️ Text to Voice
Natural speech synthesis with multiple voice options:
- Multiple voices (male/female, different accents)
- Adjustable speech rate and volume
- Support for multiple languages via Google TTS
- Save audio files in multiple formats
- **Automatic pygame installation for audio playback**

### 🖼️ Image Analysis
AI-powered image understanding with Vision Transformer:
- Deep learning feature extraction (ViT-base model)
- Text recognition (OCR) with EasyOCR
- Edge detection using OpenCV
- Color analysis and statistics
- Histogram generation
- Export analysis to JSON
- **Smart dependency installation** (Pillow, NumPy, OpenCV, EasyOCR)

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free space for application and AI models
- **Processor**: Dual-core CPU, 2.0 GHz or higher
- **Internet**: Required for first-time setup and dependency installation

### Recommended Requirements
- **RAM**: 16 GB for faster AI processing
- **Storage**: 5 GB free space
- **Processor**: Quad-core CPU, 3.0 GHz or higher
- **GPU**: CUDA-compatible GPU for faster inference (optional)

## 🚀 Installation

### Option 1: One-Click Bootstrapper (Easiest)
1. Download `bootstrapper.exe` from the [releases page](https://github.com/putbullet/TurnIT/releases)
2. Run the bootstrapper - it will automatically:
   - Clone the repository from GitHub
   - Install Python dependencies
   - Download AI models (Whisper-small, ViT-base)
   - Check for updates on each run
3. Launch TurnIT when setup completes

### Option 2: Manual Installation
```bash
# Clone the repository
git clone https://github.com/putbullet/TurnIT.git
cd TurnIT

# Install dependencies
pip install -r requirements.txt

# Run the application
python main_app.py
```

## 🎯 Key Features & Improvements (v1.0.1)

### 🔄 Automatic Dependency Management
- **Smart Installation**: Missing packages are automatically detected and installed
- **On-Demand Setup**: Features install their dependencies when first used
- **No Manual pip Commands**: Click "Yes" when prompted, and TurnIT handles the rest
- **Restart Notifications**: Clear instructions when a restart is needed

### 📦 Optimized Model Downloads
- **Smaller Models**: Whisper-small (0.5GB) instead of Whisper-large-v3 (3.1GB)
- **Faster Setup**: Models download in under 2 minutes on good connections
- **Real-Time Progress**: Setup dialog shows download status and progress
- **Offline Operation**: Once downloaded, works completely offline

### 🔄 Auto-Update System
- **GitHub Integration**: Bootstrapper checks for updates automatically
- **Smart Updates**: Stashes local changes, pulls latest code, restores changes
- **Version Control**: Always uses the latest stable release

### 🎨 Enhanced User Experience
- **Dark Theme**: Beautiful gradient UI with modern design
- **Progress Tracking**: Real-time feedback for all operations
- **Error Handling**: Graceful fallbacks and clear error messages
- **Multi-Language**: Support for 50+ languages in speech features
## 💡 How to Use

#### Voice to Text
1. Click **"Voice to Text"** from the main menu
2. Select your language (default: English)
3. Click **"Start Recording"** and speak into your microphone
4. Click **"Stop Recording"** when finished
5. Wait for AI transcription to complete
6. **Export** your text or copy to clipboard

#### Text to Speech
1. Click **"Text to Speech"** from the main menu
2. Type or paste text into the text box
3. Select voice, language, and adjust speed
4. Click **"Play"** to hear the speech
5. **Save Audio** to export as MP3/WAV file
6. *Note: First use will install pygame automatically*

#### Image Analysis
1. Click **"Image Analysis"** from the main menu
2. **Load Image** from your computer
3. Click **"Analyze"** to start AI processing
4. Switch between tabs to view:
   - **Basic Features**: Dimensions, colors, statistics
   - **AI Features**: Deep learning embeddings
   - **Edge Detection**: Canny edge detection results
   - **Color Analysis**: Histogram and color distribution
   - **OCR**: Extracted text from image
5. **Export Results** as JSON file
6. *Note: Missing packages (Pillow, OpenCV, EasyOCR) install automatically*

## 📋 Dependencies

### Core Requirements
- **Python**: 3.10 or higher
- **PySide6**: Qt6 GUI framework (6.10.1+)
- **PyTorch**: Deep learning framework (2.0.0+)
- **Transformers**: HuggingFace models (4.30.0+)

### Feature-Specific (Auto-Installed)
- **Speech Recognition**: librosa, soundfile, numpy
- **Text-to-Speech**: pygame, gtts, pyttsx3
- **Image Analysis**: Pillow, opencv-python, easyocr, matplotlib

### Optional Enhancements
- **CUDA Toolkit**: For GPU acceleration (significantly faster)
- **Git**: For auto-updates via bootstrapper

## 🔧 Technical Details

### AI Models Used
- **Speech Recognition**: OpenAI Whisper-small (0.5GB, 39M parameters)
- **Image Analysis**: Vision Transformer ViT-base (0.33GB, 86M parameters)
- **Text-to-Speech**: Google TTS + pyttsx3 (offline/online hybrid)
- **OCR**: EasyOCR (supports 80+ languages)

### Architecture
- **Frontend**: PySide6 (Qt6) with custom dark gradient theme
- **AI Framework**: PyTorch + HuggingFace Transformers
- **Audio Processing**: librosa, soundfile, pygame
- **Image Processing**: OpenCV, PIL, matplotlib, NumPy
- **Offline Operation**: All models cached locally in `models/` directory
- **Auto-Updates**: Git-based repository sync via bootstrapper

### Smart Dependency Management
- **Startup Check**: Validates all core dependencies on launch
- **On-Demand Installation**: Feature-specific packages install when needed
- **User Prompts**: Clear dialogs ask permission before installing
- **Fallback Instructions**: Manual pip commands provided if auto-install fails
- **Restart Notifications**: Tells user when restart is required

## 🔒 Privacy & Security

- **Local Processing:** All AI operations run on your device
- **No Data Collection:** No personal information is transmitted
- **Offline Capable:** Works completely offline after setup
- **User Control:** Delete all data and models at any time

## 📁 Project Structure

```
TurnIT/
├── bootstrapper.py          # One-click installer with auto-update
├── main_app.py              # Main application entry point
├── requirements.txt         # Core dependencies
├── requirements_production.txt  # Minimal production dependencies
├── ai/
│   └── model_manager.py     # AI model management
├── ui/
│   ├── startup_screen_new.py    # Startup and setup screen
│   ├── setup_dialog.py          # First-time setup with progress
│   ├── main_menu.py             # Main navigation menu
│   ├── audio_to_text_ui.py      # Speech recognition UI
│   ├── text_to_speech_ui.py     # Text-to-speech UI (auto-installs pygame)
│   └── image_analysis_ui.py     # Image analysis UI (auto-installs Pillow/OpenCV)
├── utils/
│   ├── logger.py            # Logging configuration
│   ├── app_setup.py         # Application setup utilities
│   └── dependency_checker.py # Automatic package installer
├── models/                  # AI models storage (created on first run)
└── cache/                   # Transformers cache directory
```

## 🆘 Troubleshooting

### Common Issues

**"pip install pillow" error when analyzing images**
- **Solution**: Click "Analyze" again - TurnIT will auto-install Pillow and prompt you to restart
- If auto-install fails, manually run: `pip install pillow numpy opencv-python easyocr`

**pygame error when using Text-to-Speech**
- **Solution**: Click "Play" - TurnIT will offer to install pygame automatically
- If auto-install fails, manually run: `pip install pygame`

**Models not downloading during setup**
- Check internet connection (required for first-time setup only)
- Ensure 2GB+ free disk space in TurnIT directory
- Close and rerun the bootstrapper or setup

**"Missing dependencies" on startup**
- Click "Yes" when prompted to install missing packages
- Wait for installation to complete
- Restart TurnIT after installation finishes
- If issues persist, run: `pip install -r requirements.txt`

**Performance issues / Slow AI processing**
- Close other applications during AI operations
- Reduce image size before analysis (< 2000x2000 pixels)
- Consider using GPU if available (install CUDA toolkit)
- Whisper-small is already optimized for speed

**Audio recording not working**
- **Windows**: Install PyAudio manually or use Windows Store version
- **Linux**: `sudo apt-get install python3-pyaudio portaudio19-dev`
- **macOS**: `brew install portaudio`, then `pip install pyaudio`
- Check microphone permissions in system settings

**Bootstrapper "git not found" error**
- Install Git from: https://git-scm.com/downloads
- Or clone manually: `git clone https://github.com/putbullet/TurnIT.git`

## 🔄 Updates & Changelog

### v1.0.1 (Latest)
- ✅ **Automatic dependency installation** - No more manual pip commands
- ✅ **On-demand package setup** - Features install requirements when first used
- ✅ **Optimized models** - Whisper-small (0.5GB) instead of large-v3 (3.1GB)
- ✅ **Real-time setup progress** - Visual feedback during first-time setup
- ✅ **Auto-update bootstrapper** - Checks GitHub for latest code on each run
- ✅ **Fixed pygame crashes** - Smart null checks and auto-installation
- ✅ **Fixed Pillow errors** - Dynamic import with auto-installation and reload
- ✅ **Enhanced error handling** - Graceful fallbacks and clear user messages
- ✅ **Improved UI feedback** - Progress bars, status messages, completion notifications

### v1.0.0
- Initial release with Voice-to-Text, Text-to-Speech, Image Analysis
- Qt6-based dark theme UI
- Offline AI model support

TurnIT automatically checks for updates when launched via the bootstrapper. The application works completely offline after initial setup and model downloads.

## 👨‍💻 Developer

**Created by**: putbullet  
**Version**: 1.0.1  
**License**: MIT License (Open Source)  
**Repository**: [github.com/putbullet/TurnIT](https://github.com/putbullet/TurnIT)

## 🤝 Contributing

This is an open-source project. Contributions are welcome!

**Ways to contribute**:
- 🐛 Report bugs and issues on GitHub
- 💡 Suggest new features and improvements
- 🔧 Submit pull requests with bug fixes or enhancements
- 📖 Improve documentation and examples
- ⭐ Star the repository if you find it useful

**Development Setup**:
```bash
git clone https://github.com/putbullet/TurnIT.git
cd TurnIT
pip install -r requirements.txt
python main_app.py
```

## 📞 Support

For support and questions:
1. Check the **Troubleshooting** section above
2. Review **System Requirements** to ensure compatibility
3. Open an issue on [GitHub Issues](https://github.com/putbullet/TurnIT/issues)
4. Check existing issues for similar problems and solutions

**Before reporting a bug**:
- Include your OS version and Python version
- Attach relevant error messages from logs
- Describe steps to reproduce the issue
- Mention if you're using GPU/CUDA

---

**⚡ Experience the future of offline AI desktop applications with TurnIT!**
