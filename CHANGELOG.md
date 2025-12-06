# Changelog

All notable changes to TurnIT will be documented in this file.

## [1.0.0] - 2024-12-06

### Added
- Voice to Text: Real-time audio recording with Whisper AI transcription
- Text to Voice: Natural speech synthesis with multiple voices
- Image Analysis: AI-powered image understanding with ViT model
- Multi-language support (English, Arabic, French)
- Modern diagonal gradient UI design
- Live audio level monitoring during recording
- Export transcriptions to TXT files
- Export AI analysis results to JSON
- Settings management with persistent configuration
- Comprehensive error handling and logging

### Features
- Lazy loading of AI models for faster startup
- CPU-optimized inference
- Dark theme with smooth animations
- Privacy-focused (all processing done locally)
- No internet required after initial model download

### Technical
- Built with PySide6 for modern Qt6 UI
- Whisper for speech recognition
- Vision Transformer (ViT) for image analysis
- EasyOCR for text extraction from images
- gTTS and pyttsx3 for text-to-speech
