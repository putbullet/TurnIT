# TurnIT - AI Desktop Assistant

<div align="center">

**AI-Powered Desktop Tools for Your Daily Tasks**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/putbullet/TurnIT)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.txt)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

</div>

## 🌟 Features

### 🎤 Voice to Text
Convert speech to text with state-of-the-art AI transcription using OpenAI Whisper:
- Real-time audio recording with live level monitoring
- Multiple language support
- High accuracy transcription
- Export results to TXT files

### 🗣️ Text to Voice
Natural speech synthesis with multiple voice options:
- Multiple voices (male/female, different accents)
- Adjustable speech rate
- Support for multiple languages
- Save audio files

### 🖼️ Image Analysis
AI-powered image understanding with Vision Transformer:
- Deep learning feature extraction
- Text recognition (OCR)
- Color analysis
- Object detection capabilities
- Export analysis to JSON

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free space for application and AI models
- **Processor**: Dual-core CPU, 2.0 GHz or higher

### Recommended Requirements
- **RAM**: 16 GB for faster AI processing
- **Storage**: 5 GB free space
- **Processor**: Quad-core CPU, 3.0 GHz or higher
- **GPU**: CUDA-compatible GPU for faster inference (optional)

## 🚀 Installation

### Option 1: Standalone Executable (Recommended)
1. Download the latest `TurnIT-Setup.exe` from the releases page
2. Run the installer
3. Follow the installation wizard
4. Launch TurnIT from your desktop or start menu

### Option 2: From Source
- Export transcriptions as text files
- Real-time transcription with progress indicators

#### Text to Speech
- Enter text or load from files
- Choose from multiple voice options
- Adjust speech rate and volume
- Save generated audio files

#### Image Analysis
- Load and analyze images
- Extract basic features (dimensions, colors, statistics)
- AI-powered deep learning features
- Edge detection and color analysis
- Export analysis results

## 📋 System Requirements

- **OS:** Windows 10+, macOS 10.14+, or Linux
- **Python:** 3.8 or higher
- **RAM:** 8GB minimum, 16GB recommended for large models
- **Storage:** 5GB free space for models and dependencies
- **Audio:** Microphone and speakers for audio features

## 🔧 Technical Details

### AI Models Used
- **Speech Recognition:** OpenAI Whisper (large-v3)
- **Fallback Speech:** Qwen2-Audio-7B-Instruct
- **Image Analysis:** Vision Transformer (ViT-base-patch16-224)
- **Text-to-Speech:** pyttsx3 + Google TTS integration

### Architecture
- **Frontend:** PySide6 (Qt6) with custom dark theme
- **AI Framework:** PyTorch + HuggingFace Transformers
- **Audio Processing:** librosa, pyaudio, pygame
- **Image Processing:** OpenCV, PIL, matplotlib
- **Offline Operation:** All models cached locally after download

## 🔒 Privacy & Security

- **Local Processing:** All AI operations run on your device
- **No Data Collection:** No personal information is transmitted
- **Offline Capable:** Works completely offline after setup
- **User Control:** Delete all data and models at any time

## 📁 Project Structure

```
TurnIT/
├── main_app.py              # Main application entry point
├── setup.py                 # Setup and dependency installer
├── requirements_full.txt    # Full dependency list
├── ai/
│   └── model_manager.py     # AI model management
├── ui/
│   ├── startup_screen_new.py    # Startup and setup screen
│   ├── main_menu.py             # Main navigation menu
│   ├── audio_to_text_ui.py      # Speech recognition UI
│   ├── text_to_speech_ui.py     # Text-to-speech UI
│   └── image_analysis_ui.py     # Image analysis UI
├── utils/
│   ├── logger.py            # Logging configuration
│   └── app_setup.py         # Application setup utilities
└── models/                  # AI models storage (created on first run)
```

## 🆘 Troubleshooting

### Common Issues

**ImportError: No module named 'PySide6'**
```bash
pip install PySide6
```

**Audio recording not working**
- Windows: Install PyAudio manually
- Linux: `sudo apt-get install python3-pyaudio portaudio19-dev`
- macOS: `brew install portaudio`

**Models not downloading**
- Check internet connection for first-time setup
- Ensure 5GB+ free disk space
- Try running setup again

**Performance issues**
- Close other applications during AI processing
- Consider using GPU if available (CUDA support)
- Reduce model sizes in settings

## 🔄 Updates

TurnIT checks for model updates during startup. The application is designed to work completely offline after initial setup.

## 👨‍💻 Developer

**Created by:** putbullet  
**Version:** 1.0.0  
**License:** Open Source  

## 🤝 Contributing

This is an open-source project. Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📞 Support

For support and questions:
- Check the troubleshooting section above
- Review the system requirements
- Ensure all dependencies are installed correctly

---

**⚡ Experience the future of offline AI desktop applications with TurnIT!**
