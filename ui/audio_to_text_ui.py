"""
Audio to Text UI for TurnIT
Speech recognition workflow interface
"""

import sys
import os
import logging
import threading
import time
from pathlib import Path
from typing import Optional

# Import PySide6 components
try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QTextEdit, QProgressBar,
        QFileDialog, QGroupBox, QFrame, QMessageBox, QScrollArea
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QIcon
except ImportError:
    print("PySide6 not installed. Installing...")
    # This will be handled by app_setup

# Audio processing imports
try:
    import pyaudio
    import numpy as np
    import librosa
    import soundfile as sf
    import sounddevice as sd
except ImportError:
    pyaudio = None
    np = None
    librosa = None
    sf = None
    sd = None

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from utils.global_settings import GlobalSettings
from ai.model_manager import AIModelsManager

logger = get_logger(__name__)

class AudioRecorder:
    """Handles audio recording functionality"""
    
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.audio_data = []
        self.pyaudio_instance = None
        self.stream = None
        self.level_callback = None  # For live audio level updates
    
    def set_level_callback(self, callback):
        """Set callback for live audio level updates"""
        self.level_callback = callback
    
    def get_audio_devices(self):
        """Get list of available audio input devices"""
        try:
            if pyaudio is None:
                logger.error("PyAudio not available")
                return []
                
            if self.pyaudio_instance is None:
                self.pyaudio_instance = pyaudio.PyAudio()
            
            devices = []
            info = self.pyaudio_instance.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            for i in range(0, num_devices):
                device_info = self.pyaudio_instance.get_device_info_by_host_api_device_index(0, i)
                if device_info.get('maxInputChannels') > 0:
                    devices.append({
                        'index': i,
                        'name': device_info.get('name'),
                        'channels': device_info.get('maxInputChannels')
                    })
            
            return devices
        except Exception as e:
            logger.error(f"Error getting audio devices: {str(e)}")
            return []
    
    def start_recording(self, device_index=None):
        """Start audio recording"""
        try:
            if pyaudio is None:
                logger.error("PyAudio not available")
                return False
                
            if self.pyaudio_instance is None:
                self.pyaudio_instance = pyaudio.PyAudio()
            
            # Try to open stream with error handling
            try:
                self.stream = self.pyaudio_instance.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=self.chunk,
                    stream_callback=None  # We'll use blocking mode for simplicity
                )
            except Exception as stream_error:
                logger.error(f"Error opening audio stream: {str(stream_error)}")
                # Try with default device
                self.stream = self.pyaudio_instance.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk
                )
            
            self.recording = True
            self.audio_data = []
            logger.info("Audio recording started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            return False
    
    def record_chunk(self):
        """Record a single audio chunk and return audio level"""
        if self.recording and self.stream:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                # Calculate audio level (RMS)
                if len(audio_chunk) > 0:
                    # Convert to float to avoid overflow issues
                    audio_float = audio_chunk.astype(np.float32)
                    # Calculate RMS with safety check
                    mean_square = np.mean(audio_float ** 2)
                    if mean_square > 0:
                        audio_level = np.sqrt(mean_square)
                        # Normalize to 0-100 range
                        audio_level = min(100, (audio_level / 1000) * 100)
                    else:
                        audio_level = 0
                    
                    # Call level callback if set
                    if self.level_callback:
                        self.level_callback(audio_level)
                    
                    self.audio_data.append(audio_chunk)
                    return audio_chunk, audio_level
                    
            except Exception as e:
                logger.error(f"Error recording chunk: {str(e)}")
                return None, 0
        return None, 0
    
    def stop_recording(self):
        """Stop audio recording and return audio data"""
        try:
            self.recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if len(self.audio_data) > 0:
                audio_array = np.concatenate(self.audio_data)
                # Normalize to float32 for model input
                audio_float = audio_array.astype(np.float32) / 32768.0
                
                # Check if audio has actual content (not just silence)
                audio_power = np.mean(audio_float ** 2)
                if audio_power < 1e-6:  # Very quiet threshold
                    logger.warning("Audio appears to be silent")
                
                logger.info(f"Recording stopped. Audio length: {len(audio_float)/self.rate:.2f} seconds, Power: {audio_power:.6f}")
                return audio_float
            else:
                logger.warning("No audio data recorded")
                return None
                
        except Exception as e:
            logger.error(f"Error stopping recording: {str(e)}")
            return None
    
    def cleanup(self):
        """Cleanup audio resources"""
        self.recording = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except:
                pass
            self.pyaudio_instance = None

class TranscriptionThread(QThread):
    """Thread for handling audio transcription"""
    transcription_complete = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, audio_data, models_manager, language="en"):
        super().__init__()
        self.audio_data = audio_data
        self.models_manager = models_manager
        self.language = language
    
    def run(self):
        """Run transcription in separate thread"""
        try:
            transcription = self.models_manager.transcribe_audio(
                self.audio_data, 
                sample_rate=16000, 
                language=self.language
            )
            self.transcription_complete.emit(transcription)
        except Exception as e:
            self.error_occurred.emit(str(e))

class AudioToTextWindow(QMainWindow):
    """Audio to Text conversion interface"""
    
    def __init__(self):
        super().__init__()
        self.current_language = GlobalSettings().get_language()
        self.recorder = AudioRecorder()
        self.models_manager = None
        self.transcription_thread = None
        self.recording_timer = QTimer()
        self.recording_time = 0
        
        # Audio level monitoring timer (faster update)
        self.audio_monitor_timer = QTimer()
        self.audio_monitor_timer.timeout.connect(self.update_audio_level)
        
        # Set up audio level callback
        self.recorder.set_level_callback(self.on_audio_level_update)
        
        # Load models
        self.init_models()
        self.init_ui()
        self.setup_connections()
        self.load_audio_devices()
        
        # Connect to global language changes
        GlobalSettings().language_changed.connect(self.on_language_changed)
    
    def init_models(self):
        """Initialize AI models manager (lazy loading)"""
        try:
            models_dir = Path(__file__).parent.parent / "models"
            self.models_manager = AIModelsManager(str(models_dir))
            # Don't load models immediately - load when needed
            logger.info("Models manager initialized (lazy loading)")
        except Exception as e:
            logger.error(f"Error initializing models manager: {str(e)}")
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("TurnIT - Audio to Text")
        self.setFixedSize(800, 700)
        self.center_window()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create sections
        self.create_header_section(main_layout)
        self.create_device_section(main_layout)
        self.create_recording_section(main_layout)
        self.create_results_section(main_layout)
        self.create_actions_section(main_layout)
        
        self.apply_dark_theme()
    
    def create_header_section(self, layout):
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Audio to Text")
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
    
    def create_device_section(self, layout):
        """Create device selection section"""
        device_group = QGroupBox("Audio Configuration")
        device_group.setStyleSheet("""
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
        
        device_layout = QVBoxLayout(device_group)
        
        # Device selection row
        device_row = QHBoxLayout()
        device_row.addWidget(QLabel("Microphone:"))
        
        self.device_combo = QComboBox()
        self.device_combo.setStyleSheet("""
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
        device_row.addWidget(self.device_combo)
        device_row.addStretch()
        device_layout.addLayout(device_row)
        
        # Language selection row
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Language:"))
        
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "English (en)", "Spanish (es)", "French (fr)", "German (de)",
            "Italian (it)", "Portuguese (pt)", "Russian (ru)", "Chinese (zh)",
            "Japanese (ja)", "Korean (ko)", "Arabic (ar)", "Dutch (nl)"
        ])
        self.language_combo.setStyleSheet(self.device_combo.styleSheet())
        lang_row.addWidget(self.language_combo)
        lang_row.addStretch()
        device_layout.addLayout(lang_row)
        
        # Confirm button
        self.confirm_btn = QPushButton("Confirm Configuration")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background: #00d4ff;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background: #00b8e6;
            }
            QPushButton:pressed {
                background: #0095cc;
            }
            QPushButton:disabled {
                background: #404040;
                color: #808080;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm_configuration)
        device_layout.addWidget(self.confirm_btn)
        
        layout.addWidget(device_group)
    
    def create_recording_section(self, layout):
        """Create recording controls section"""
        recording_group = QGroupBox("Recording")
        recording_group.setStyleSheet("""
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
        
        recording_layout = QVBoxLayout(recording_group)
        
        # Recording status and timer
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready to record")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-family: monospace;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        status_layout.addWidget(self.timer_label)
        recording_layout.addLayout(status_layout)
        
        # Audio level indicator
        level_layout = QHBoxLayout()
        
        level_label = QLabel("Audio Level:")
        level_label.setStyleSheet("""
            QLabel {
                color: #a0a0a0;
                font-size: 12px;
            }
        """)
        level_layout.addWidget(level_label)
        
        # Audio level bar
        self.audio_level_bar = QProgressBar()
        self.audio_level_bar.setMaximum(100)
        self.audio_level_bar.setValue(0)
        self.audio_level_bar.setFixedHeight(15)
        self.audio_level_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 7px;
                background: #1a1a1a;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00ff00, stop: 0.7 #ffff00, stop: 1 #ff0000);
                border-radius: 6px;
            }
        """)
        level_layout.addWidget(self.audio_level_bar)
        
        # Audio level indicator light
        self.audio_indicator = QLabel("●")
        self.audio_indicator.setFixedSize(20, 20)
        self.audio_indicator.setAlignment(Qt.AlignCenter)
        self.audio_indicator.setStyleSheet("""
            QLabel {
                color: #404040;
                font-size: 16px;
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 10px;
            }
        """)
        level_layout.addWidget(self.audio_indicator)
        
        recording_layout.addLayout(level_layout)
        
        # Recording button
        self.record_btn = QPushButton("🎤 Start Recording")
        self.record_btn.setFixedHeight(50)
        self.record_btn.setEnabled(False)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: #404040;
                color: #808080;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 25px;
                margin: 10px 0;
            }
            QPushButton:enabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00d4ff, stop: 1 #7b68ee);
                color: white;
            }
            QPushButton:enabled:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00b8e6, stop: 1 #6a5bdb);
            }
            QPushButton:enabled:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0095cc, stop: 1 #5a4bc8);
            }
        """)
        self.record_btn.clicked.connect(self.toggle_recording)
        recording_layout.addWidget(self.record_btn)
        
        layout.addWidget(recording_group)
    
    def create_results_section(self, layout):
        """Create transcription results section"""
        results_group = QGroupBox("Transcription Results")
        results_group.setStyleSheet("""
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
        
        results_layout = QVBoxLayout(results_group)
        
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
        results_layout.addWidget(self.progress_bar)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setPlaceholderText("Transcription will appear here...")
        self.results_text.setMinimumHeight(200)
        self.results_text.setStyleSheet("""
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
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
    
    def create_actions_section(self, layout):
        """Create action buttons section"""
        actions_layout = QHBoxLayout()
        
        # Load file button
        load_btn = QPushButton("📁 Load Audio File")
        load_btn.setStyleSheet("""
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
        """)
        load_btn.clicked.connect(self.load_audio_file)
        actions_layout.addWidget(load_btn)
        
        actions_layout.addStretch()
        
        # Save button
        self.save_btn = QPushButton("💾 Save as TXT")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet(load_btn.styleSheet())
        self.save_btn.clicked.connect(self.save_transcription)
        actions_layout.addWidget(self.save_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setStyleSheet(load_btn.styleSheet())
        clear_btn.clicked.connect(self.clear_results)
        actions_layout.addWidget(clear_btn)
        
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
        self.recording_timer.timeout.connect(self.update_recording_timer)
    
    def center_window(self):
        """Center window on screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def load_audio_devices(self):
        """Load available audio devices"""
        devices = self.recorder.get_audio_devices()
        self.device_combo.clear()
        
        if not devices:
            self.device_combo.addItem("No audio devices found")
            self.device_combo.setEnabled(False)
            self.confirm_btn.setEnabled(False)
        else:
            for device in devices:
                self.device_combo.addItem(f"{device['name']} ({device['channels']} channels)")
            self.device_combo.setEnabled(True)
            self.confirm_btn.setEnabled(True)
    
    def confirm_configuration(self):
        """Confirm audio configuration"""
        if self.device_combo.currentIndex() >= 0:
            self.record_btn.setEnabled(True)
            self.device_combo.setEnabled(False)
            self.language_combo.setEnabled(False)
            self.confirm_btn.setEnabled(False)
            
            self.status_label.setText("Configuration confirmed - Ready to record")
            self.status_label.setStyleSheet("QLabel { color: #00ff00; font-weight: bold; }")
            
            logger.info(f"Audio configuration confirmed: device={self.device_combo.currentText()}, language={self.language_combo.currentText()}")
    
    def on_language_changed(self, language):
        """Handle global language change"""
        self.current_language = language
        self.setWindowTitle(f"Audio to Text - {language.upper()}")
        logger.info(f"Audio window language changed to: {language}")
    
    def toggle_recording(self):
        """Toggle recording state"""
        if not self.recorder.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start audio recording"""
        device_index = self.device_combo.currentIndex()
        
        if self.recorder.start_recording(device_index):
            self.record_btn.setText("⏹️ Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #ff6b6b, stop: 1 #ff4757);
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border: none;
                    border-radius: 25px;
                    margin: 10px 0;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #ff5252, stop: 1 #ff3742);
                }
            """)
            
            self.status_label.setText("Recording...")
            self.status_label.setStyleSheet("QLabel { color: #ff6b6b; font-weight: bold; }")
            
            self.recording_time = 0
            self.recording_timer.start(1000)  # Update every second
            self.audio_monitor_timer.start(100)  # Monitor audio level every 100ms
            
            logger.info("Recording started")
    
    def stop_recording(self):
        """Stop audio recording"""
        self.recording_timer.stop()
        self.audio_monitor_timer.stop()
        
        # Reset audio level indicators
        self.audio_level_bar.setValue(0)
        self.audio_indicator.setStyleSheet("""
            QLabel {
                color: #404040;
                font-size: 16px;
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 10px;
            }
        """)
        
        audio_data = self.recorder.stop_recording()
        
        self.record_btn.setText("🎤 Start Recording")
        self.record_btn.setStyleSheet("""
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
        """)
        
        if audio_data is not None:
            self.status_label.setText("Processing audio...")
            self.status_label.setStyleSheet("QLabel { color: #ffa500; font-weight: bold; }")
            self.progress_bar.show()
            
            # Start transcription in separate thread
            language = self.language_combo.currentText().split("(")[1].split(")")[0]
            self.start_transcription(audio_data, language)
        else:
            self.status_label.setText("Recording failed")
            self.status_label.setStyleSheet("QLabel { color: #ff6b6b; font-weight: bold; }")
    
    def start_transcription(self, audio_data, language):
        """Start audio transcription"""
        if self.models_manager is None:
            self.show_error("Models not loaded. Please restart the application.")
            return
        
        self.transcription_thread = TranscriptionThread(audio_data, self.models_manager, language)
        self.transcription_thread.transcription_complete.connect(self.on_transcription_complete)
        self.transcription_thread.error_occurred.connect(self.on_transcription_error)
        self.transcription_thread.start()
    
    def on_transcription_complete(self, transcription):
        """Handle completed transcription"""
        self.progress_bar.hide()
        self.results_text.setPlainText(transcription)
        self.save_btn.setEnabled(True)
        
        self.status_label.setText("Transcription complete")
        self.status_label.setStyleSheet("QLabel { color: #00ff00; font-weight: bold; }")
        
        logger.info(f"Transcription completed: {len(transcription)} characters")
    
    def on_transcription_error(self, error):
        """Handle transcription error"""
        self.progress_bar.hide()
        self.show_error(f"Transcription failed: {error}")
        
        self.status_label.setText("Transcription failed")
        self.status_label.setStyleSheet("QLabel { color: #ff6b6b; font-weight: bold; }")
    
    def update_recording_timer(self):
        """Update recording timer display"""
        self.recording_time += 1
        minutes = self.recording_time // 60
        seconds = self.recording_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def load_audio_file(self):
        """Load audio file for transcription"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.m4a *.flac *.ogg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.status_label.setText("Loading audio file...")
                self.status_label.setStyleSheet("QLabel { color: #ffa500; font-weight: bold; }")
                self.progress_bar.show()
                
                # Load audio file
                audio_data, sample_rate = librosa.load(file_path, sr=16000)
                
                # Start transcription
                language = self.language_combo.currentText().split("(")[1].split(")")[0]
                self.start_transcription(audio_data, language)
                
                logger.info(f"Audio file loaded: {file_path}")
                
            except Exception as e:
                self.progress_bar.hide()
                self.show_error(f"Failed to load audio file: {str(e)}")
    
    def save_transcription(self):
        """Save transcription to file"""
        if not self.results_text.toPlainText().strip():
            self.show_error("No transcription to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            "transcription.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.toPlainText())
                
                self.status_label.setText(f"Saved to {os.path.basename(file_path)}")
                self.status_label.setStyleSheet("QLabel { color: #00ff00; font-weight: bold; }")
                
                logger.info(f"Transcription saved to: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def clear_results(self):
        """Clear transcription results"""
        self.results_text.clear()
        self.save_btn.setEnabled(False)
        self.status_label.setText("Results cleared")
        self.status_label.setStyleSheet("QLabel { color: #00d4ff; font-weight: bold; }")
    
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
    
    def on_audio_level_update(self, level):
        """Handle audio level updates from recorder"""
        self.audio_level_bar.setValue(int(level))
        
        # Update indicator color based on level
        if level > 50:
            color = "#00ff00"  # Green for good level
        elif level > 20:
            color = "#ffff00"  # Yellow for medium level
        elif level > 5:
            color = "#ff9900"  # Orange for low level
        else:
            color = "#404040"  # Gray for no signal
        
        self.audio_indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 10px;
            }}
        """)
    
    def update_audio_level(self):
        """Update audio level during recording"""
        if self.recorder.recording:
            chunk, level = self.recorder.record_chunk()
            if chunk is not None:
                self.on_audio_level_update(level)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.recorder.recording:
            self.recorder.stop_recording()
        
        self.recorder.cleanup()
        
        if self.transcription_thread and self.transcription_thread.isRunning():
            self.transcription_thread.quit()
            self.transcription_thread.wait()
        
        event.accept()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = AudioToTextWindow()
    window.show()
    sys.exit(app.exec())
