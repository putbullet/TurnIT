"""
Text to Speech UI for TurnIT
Text to speech conversion interface
"""

import sys
import os
import threading
import json
from pathlib import Path
from typing import Optional

# Import PySide6 components
try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QTextEdit, QProgressBar,
        QFileDialog, QGroupBox, QFrame, QMessageBox, QScrollArea,
        QSlider, QSpinBox, QCheckBox
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QIcon
except ImportError:
    print("PySide6 not installed. Installing...")

# Text-to-Speech imports
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    import pygame
except ImportError:
    pygame = None

try:
    import io
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError:
    io = None
    AudioSegment = None
    play = None

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from utils.global_settings import GlobalSettings

logger = get_logger(__name__)

class TTSEngine:
    """Text-to-Speech engine wrapper"""
    
    def __init__(self):
        self.pyttsx_engine = None
        self.init_pyttsx3()
        self.output_file = None
        self.pygame_available = False
        
        if pygame is not None:
            try:
                pygame.mixer.init()
                self.pygame_available = True
                logger.info("pygame audio playback initialized")
            except Exception as e:
                logger.warning(f"pygame mixer initialization failed: {str(e)}")
                self.pygame_available = False
        else:
            logger.warning("pygame not available - audio playback may not work")
    
    def init_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        if pyttsx3 is None:
            logger.error("pyttsx3 not installed. Please install: pip install pyttsx3")
            return
            
        try:
            self.pyttsx_engine = pyttsx3.init()
            logger.info("pyttsx3 engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {str(e)}")
    
    def get_voices(self):
        """Get available voices"""
        voices = []
        
        if self.pyttsx_engine:
            try:
                engine_voices = self.pyttsx_engine.getProperty('voices')
                for i, voice in enumerate(engine_voices):
                    voice_name = voice.name if hasattr(voice, 'name') else f"Voice {i+1}"
                    voice_id = voice.id if hasattr(voice, 'id') else str(i)
                    voice_gender = "Unknown"
                    
                    # Try to determine gender from voice name
                    name_lower = voice_name.lower()
                    if any(word in name_lower for word in ['female', 'woman', 'lady', 'zira', 'cortana', 'susan', 'samantha']):
                        voice_gender = "Female"
                    elif any(word in name_lower for word in ['male', 'man', 'david', 'mark', 'richard', 'daniel']):
                        voice_gender = "Male"
                    
                    voices.append({
                        'id': voice_id,
                        'name': voice_name,
                        'gender': voice_gender,
                        'engine': 'pyttsx3'
                    })
            except Exception as e:
                logger.error(f"Error getting voices: {str(e)}")
        
        # Add gTTS options
        gtts_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi'
        }
        
        for lang_code, lang_name in gtts_languages.items():
            voices.append({
                'id': f"gtts_{lang_code}",
                'name': f"Google TTS - {lang_name}",
                'gender': "Neural",
                'engine': 'gtts'
            })
        
        return voices
    
    def synthesize_speech(self, text, voice_id=None, rate=200, volume=1.0, save_path=None):
        """Synthesize text to speech"""
        try:
            if voice_id and voice_id.startswith("gtts_"):
                return self._synthesize_gtts(text, voice_id, save_path)
            else:
                return self._synthesize_pyttsx3(text, voice_id, rate, volume, save_path)
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            raise e
    
    def _synthesize_pyttsx3(self, text, voice_id, rate, volume, save_path):
        """Synthesize using pyttsx3"""
        if not self.pyttsx_engine:
            raise Exception("pyttsx3 engine not available")
        
        # Set voice
        if voice_id:
            voices = self.pyttsx_engine.getProperty('voices')
            for voice in voices:
                if voice.id == voice_id:
                    self.pyttsx_engine.setProperty('voice', voice_id)
                    break
        
        # Set rate and volume
        self.pyttsx_engine.setProperty('rate', rate)
        self.pyttsx_engine.setProperty('volume', volume)
        
        if save_path:
            self.pyttsx_engine.save_to_file(text, save_path)
            self.pyttsx_engine.runAndWait()
            return save_path
        else:
            # Generate temporary file for playback
            temp_path = Path.cwd() / "temp_speech.wav"
            self.pyttsx_engine.save_to_file(text, str(temp_path))
            self.pyttsx_engine.runAndWait()
            self.output_file = str(temp_path)
            return str(temp_path)
    
    def _synthesize_gtts(self, text, voice_id, save_path):
        """Synthesize using Google TTS"""
        if gTTS is None:
            raise Exception("Google TTS not available. Please install: pip install gtts")
            
        lang_code = voice_id.replace("gtts_", "")
        
        try:
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            if save_path:
                tts.save(save_path)
                return save_path
            else:
                # Save to temporary file with unique name
                import time
                timestamp = int(time.time() * 1000)
                temp_path = Path.cwd() / f"temp_gtts_speech_{timestamp}.mp3"
                tts.save(str(temp_path))
                self.output_file = str(temp_path)
                return str(temp_path)
                
        except Exception as e:
            raise Exception(f"Google TTS failed: {str(e)}")
    
    def play_audio(self, audio_path):
        """Play audio file"""
        try:
            if pygame is None or pygame.mixer is None:
                logger.error("pygame not available for audio playback")
                return False
            
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            return True
        except Exception as e:
            logger.error(f"Audio playback failed: {str(e)}")
            return False
    
    def stop_audio(self):
        """Stop audio playback"""
        try:
            if pygame is not None and pygame.mixer is not None:
                pygame.mixer.music.stop()
        except Exception as e:
            logger.error(f"Error stopping audio: {str(e)}")
    
    def is_playing(self):
        """Check if audio is playing"""
        try:
            if pygame is None or pygame.mixer is None:
                return False
            return pygame.mixer.music.get_busy()
        except Exception as e:
            logger.error(f"Error checking playback status: {str(e)}")
            return False

class SynthesisThread(QThread):
    """Thread for handling speech synthesis"""
    synthesis_complete = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, text, tts_engine, voice_id, rate, volume, save_path=None):
        super().__init__()
        self.text = text
        self.tts_engine = tts_engine
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        self.save_path = save_path
    
    def run(self):
        """Run synthesis in separate thread"""
        try:
            output_path = self.tts_engine.synthesize_speech(
                self.text, self.voice_id, self.rate, self.volume, self.save_path
            )
            self.synthesis_complete.emit(output_path)
        except Exception as e:
            self.error_occurred.emit(str(e))

class TextToSpeechWindow(QMainWindow):
    """Text to Speech conversion interface"""
    
    def __init__(self):
        super().__init__()
        self.current_language = GlobalSettings().get_language()
        self.tts_engine = TTSEngine()
        self.synthesis_thread = None
        self.current_audio_path = None
        self.temp_files = []  # Track temp files for cleanup
        
        self.init_ui()
        self.setup_connections()
        self.load_voices()
        
        # Connect to global language changes
        GlobalSettings().language_changed.connect(self.on_language_changed)
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("TurnIT - Text to Speech")
        self.setFixedSize(800, 750)
        self.center_window()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create sections
        self.create_header_section(main_layout)
        self.create_text_input_section(main_layout)
        self.create_voice_settings_section(main_layout)
        self.create_synthesis_section(main_layout)
        self.create_playback_section(main_layout)
        self.create_actions_section(main_layout)
        
        self.apply_dark_theme()
    
    def create_header_section(self, layout):
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Text to Speech")
        title_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
    
    def create_text_input_section(self, layout):
        """Create text input section"""
        text_group = QGroupBox("Text Input")
        text_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 10px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        text_layout = QVBoxLayout(text_group)
        
        # Text input area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to convert to speech...")
        self.text_input.setMinimumHeight(120)
        self.text_input.setMaximumHeight(150)
        self.text_input.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #e0e0e0;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        text_layout.addWidget(self.text_input)
        
        # Text controls
        text_controls = QHBoxLayout()
        
        # Character count
        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setStyleSheet("color: #808080; font-size: 12px;")
        text_controls.addWidget(self.char_count_label)
        
        text_controls.addStretch()
        
        # Load text file button
        load_text_btn = QPushButton("📄 Load Text File")
        load_text_btn.setStyleSheet("""
            QPushButton {
                background: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #404040;
                border-color: #00d4ff;
            }
        """)
        load_text_btn.clicked.connect(self.load_text_file)
        text_controls.addWidget(load_text_btn)
        
        # Clear button
        clear_text_btn = QPushButton("🗑️ Clear")
        clear_text_btn.setStyleSheet(load_text_btn.styleSheet())
        clear_text_btn.clicked.connect(self.clear_text)
        text_controls.addWidget(clear_text_btn)
        
        text_layout.addLayout(text_controls)
        layout.addWidget(text_group)
    
    def create_voice_settings_section(self, layout):
        """Create voice settings section"""
        voice_group = QGroupBox("Voice Settings")
        voice_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 10px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        voice_layout = QVBoxLayout(voice_group)
        
        # Voice selection
        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("Voice:"))
        
        self.voice_combo = QComboBox()
        self.voice_combo.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 8px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00d4ff;
            }
        """)
        voice_row.addWidget(self.voice_combo)
        voice_row.addStretch()
        voice_layout.addLayout(voice_row)
        
        # Speech rate
        rate_row = QHBoxLayout()
        rate_row.addWidget(QLabel("Speed:"))
        
        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setRange(50, 300)
        self.rate_slider.setValue(200)
        self.rate_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 8px;
                background: #2a2a2a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00d4ff;
                border: 1px solid #00b8e6;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #00d4ff;
                border-radius: 4px;
            }
        """)
        rate_row.addWidget(self.rate_slider)
        
        self.rate_label = QLabel("200")
        self.rate_label.setFixedWidth(40)
        self.rate_label.setStyleSheet("color: #00d4ff; font-weight: bold;")
        rate_row.addWidget(self.rate_label)
        
        voice_layout.addLayout(rate_row)
        
        # Volume
        volume_row = QHBoxLayout()
        volume_row.addWidget(QLabel("Volume:"))
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setStyleSheet(self.rate_slider.styleSheet())
        volume_row.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("100%")
        self.volume_label.setFixedWidth(40)
        self.volume_label.setStyleSheet("color: #00d4ff; font-weight: bold;")
        volume_row.addWidget(self.volume_label)
        
        voice_layout.addLayout(volume_row)
        
        layout.addWidget(voice_group)
    
    def create_synthesis_section(self, layout):
        """Create synthesis section"""
        synthesis_group = QGroupBox("Speech Synthesis")
        synthesis_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 10px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        synthesis_layout = QVBoxLayout(synthesis_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                background: #2a2a2a;
                height: 20px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00d4ff, stop: 1 #7b68ee);
                border-radius: 6px;
            }
        """)
        synthesis_layout.addWidget(self.progress_bar)
        
        # Synthesis button
        self.synthesize_btn = QPushButton("🎯 Generate Speech")
        self.synthesize_btn.setFixedHeight(50)
        self.synthesize_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00d4ff, stop: 1 #7b68ee);
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 25px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00b8e6, stop: 1 #6a5bdb);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0095cc, stop: 1 #5a4bc8);
            }
            QPushButton:disabled {
                background: #404040;
                color: #808080;
            }
        """)
        self.synthesize_btn.clicked.connect(self.synthesize_speech)
        synthesis_layout.addWidget(self.synthesize_btn)
        
        layout.addWidget(synthesis_group)
    
    def create_playback_section(self, layout):
        """Create playback controls section"""
        playback_group = QGroupBox("Playback")
        playback_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 10px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        playback_layout = QVBoxLayout(playback_group)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.setEnabled(False)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background: #404040;
                color: #808080;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:enabled {
                background: #00d4ff;
                color: white;
            }
            QPushButton:enabled:hover {
                background: #00b8e6;
            }
        """)
        self.play_btn.clicked.connect(self.play_audio)
        controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(self.play_btn.styleSheet())
        self.stop_btn.clicked.connect(self.stop_audio)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        
        # Status label
        self.status_label = QLabel("No audio generated")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-style: italic;
            }
        """)
        controls_layout.addWidget(self.status_label)
        
        playback_layout.addLayout(controls_layout)
        layout.addWidget(playback_group)
    
    def create_actions_section(self, layout):
        """Create action buttons section"""
        actions_layout = QHBoxLayout()
        
        # Save audio button
        self.save_btn = QPushButton("💾 Save Audio")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #2a2a2a;
                color: #e0e0e0;
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background: #404040;
                border-color: #00d4ff;
            }
            QPushButton:disabled {
                background: #1a1a1a;
                color: #606060;
                border-color: #303030;
            }
        """)
        self.save_btn.clicked.connect(self.save_audio)
        actions_layout.addWidget(self.save_btn)
        
        actions_layout.addStretch()
        
        # Reset button
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.setStyleSheet(self.save_btn.styleSheet())
        reset_btn.clicked.connect(self.reset_interface)
        actions_layout.addWidget(reset_btn)
        
        layout.addLayout(actions_layout)
    
    def apply_dark_theme(self):
        """Apply dark theme to window"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1a1a1a, stop: 0.5 #2a2a2a, stop: 1 #1a1a1a);
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.text_input.textChanged.connect(self.update_char_count)
        self.rate_slider.valueChanged.connect(self.update_rate_label)
        self.volume_slider.valueChanged.connect(self.update_volume_label)
    
    def center_window(self):
        """Center window on screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def load_voices(self):
        """Load available voices"""
        try:
            voices = self.tts_engine.get_voices()
            self.voice_combo.clear()
            
            for voice in voices:
                display_text = f"{voice['name']} ({voice['gender']}) - {voice['engine']}"
                self.voice_combo.addItem(display_text, voice['id'])
            
            logger.info(f"Loaded {len(voices)} voices")
            
        except Exception as e:
            logger.error(f"Error loading voices: {str(e)}")
            self.voice_combo.addItem("Default Voice", "default")
    
    def on_language_changed(self, language):
        """Handle global language change"""
        self.current_language = language
        self.setWindowTitle(f"Text to Speech - {language.upper()}")
        logger.info(f"TTS window language changed to: {language}")
    
    def update_char_count(self):
        """Update character count"""
        text = self.text_input.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"{char_count} characters")
        
        # Enable/disable synthesis button based on text
        self.synthesize_btn.setEnabled(char_count > 0)
    
    def update_rate_label(self, value):
        """Update rate label"""
        self.rate_label.setText(str(value))
    
    def update_volume_label(self, value):
        """Update volume label"""
        self.volume_label.setText(f"{value}%")
    
    def load_text_file(self):
        """Load text from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Text File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                self.text_input.setPlainText(text)
                self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
                self.status_label.setStyleSheet("QLabel { color: #00ff00; }")
                
                logger.info(f"Text loaded from: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to load file: {str(e)}")
    
    def clear_text(self):
        """Clear text input"""
        self.text_input.clear()
        self.status_label.setText("Text cleared")
        self.status_label.setStyleSheet("QLabel { color: #00d4ff; }")
    
    def synthesize_speech(self):
        """Synthesize text to speech"""
        text = self.text_input.toPlainText().strip()
        
        if not text:
            self.show_error("Please enter some text to synthesize.")
            return
        
        # Get settings
        voice_id = self.voice_combo.currentData()
        rate = self.rate_slider.value()
        volume = self.volume_slider.value() / 100.0
        
        # Show progress
        self.progress_bar.show()
        self.synthesize_btn.setEnabled(False)
        self.status_label.setText("Generating speech...")
        self.status_label.setStyleSheet("QLabel { color: #ffa500; }")
        
        # Start synthesis thread
        self.synthesis_thread = SynthesisThread(text, self.tts_engine, voice_id, rate, volume)
        self.synthesis_thread.synthesis_complete.connect(self.on_synthesis_complete)
        self.synthesis_thread.error_occurred.connect(self.on_synthesis_error)
        self.synthesis_thread.start()
    
    def on_synthesis_complete(self, audio_path):
        """Handle completed synthesis"""
        self.progress_bar.hide()
        self.synthesize_btn.setEnabled(True)
        
        self.current_audio_path = audio_path
        self.play_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        
        self.status_label.setText("Speech generated successfully")
        self.status_label.setStyleSheet("QLabel { color: #00ff00; }")
        
        logger.info(f"Speech synthesis completed: {audio_path}")
    
    def on_synthesis_error(self, error):
        """Handle synthesis error"""
        self.progress_bar.hide()
        self.synthesize_btn.setEnabled(True)
        
        self.show_error(f"Speech synthesis failed: {error}")
        
        self.status_label.setText("Synthesis failed")
        self.status_label.setStyleSheet("QLabel { color: #ff6b6b; }")
    
    def play_audio(self):
        """Play generated audio"""
        if not self.current_audio_path:
            return
        
        # Check if pygame is available
        if not self.tts_engine.pygame_available:
            self.show_error("Audio playback not available. Please install pygame: pip install pygame")
            return
        
        if self.tts_engine.is_playing():
            self.tts_engine.stop_audio()
        
        if self.tts_engine.play_audio(self.current_audio_path):
            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Playing audio...")
            self.status_label.setStyleSheet("QLabel { color: #00d4ff; }")
            
            # Use timer to check when playback finishes
            self.playback_timer = QTimer()
            self.playback_timer.timeout.connect(self.check_playback_status)
            self.playback_timer.start(100)
        else:
            self.show_error("Failed to play audio. The file was generated but cannot be played.")
    
    def stop_audio(self):
        """Stop audio playback"""
        self.tts_engine.stop_audio()
        
        if hasattr(self, 'playback_timer'):
            self.playback_timer.stop()
        
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Playback stopped")
        self.status_label.setStyleSheet("QLabel { color: #808080; }")
    
    def check_playback_status(self):
        """Check if audio is still playing"""
        if not self.tts_engine.is_playing():
            self.stop_audio()
            self.status_label.setText("Playback finished")
    
    def save_audio(self):
        """Save audio to file"""
        if not self.current_audio_path:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Audio",
            "speech.wav",
            "WAV Files (*.wav);;MP3 Files (*.mp3);;All Files (*)"
        )
        
        if file_path:
            try:
                # Copy the audio file
                import shutil
                shutil.copy2(self.current_audio_path, file_path)
                
                self.status_label.setText(f"Saved: {os.path.basename(file_path)}")
                self.status_label.setStyleSheet("QLabel { color: #00ff00; }")
                
                logger.info(f"Audio saved to: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to save audio: {str(e)}")
    
    def reset_interface(self):
        """Reset the interface"""
        self.text_input.clear()
        self.rate_slider.setValue(200)
        self.volume_slider.setValue(100)
        
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        self.current_audio_path = None
        
        self.status_label.setText("Interface reset")
        self.status_label.setStyleSheet("QLabel { color: #00d4ff; }")
        
        try:
            if self.tts_engine and self.tts_engine.is_playing():
                self.tts_engine.stop_audio()
        except Exception as e:
            logger.error(f"Error stopping audio on reset: {str(e)}")
    
    def show_error(self, message):
        """Show error message"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText("An error occurred")
        msg.setInformativeText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.setStyleSheet("""
            QMessageBox {
                background: #2a2a2a;
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                background: #ff6b6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: #ff5252;
            }
        """)
        msg.exec()
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            if self.tts_engine and self.tts_engine.is_playing():
                self.tts_engine.stop_audio()
        except Exception as e:
            logger.error(f"Error stopping audio on close: {str(e)}")
        
        if self.synthesis_thread and self.synthesis_thread.isRunning():
            self.synthesis_thread.quit()
            self.synthesis_thread.wait()
        
        # Clean up temporary files with retry logic
        try:
            import time
            import glob
            # Find all temp speech files
            temp_patterns = ["temp_speech*.wav", "temp_gtts_speech*.mp3"]
            for pattern in temp_patterns:
                for temp_file in glob.glob(str(Path.cwd() / pattern)):
                    temp_path = Path(temp_file)
                    if temp_path.exists():
                        # Try multiple times with delay
                        for attempt in range(3):
                            try:
                                time.sleep(0.2)  # Give time for file release
                                temp_path.unlink()
                                break
                            except PermissionError:
                                if attempt == 2:
                                    logger.warning(f"Could not delete: {temp_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
        
        event.accept()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = TextToSpeechWindow()
    window.show()
    sys.exit(app.exec())
