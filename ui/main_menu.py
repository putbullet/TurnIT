"""
TurnIT Main Menu UI - Exact UI2 Match
Modern main menu with diagonal gradient background and 3x3 feature grid
"""

import sys
import logging
import webbrowser
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QLinearGradient

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from utils.global_settings import GlobalSettings

logger = get_logger(__name__)


class DiagonalGradientWidget(QWidget):
    """Widget with smooth diagonal gradient background"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paintEvent(self, event):
        """Paint smooth diagonal gradient"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create diagonal gradient from top-left to bottom-right
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#2a2a2a"))  # Darker at top-left
        gradient.setColorAt(1, QColor("#1a1a1a"))  # Darker at bottom-right
        
        painter.fillRect(self.rect(), gradient)
        painter.end()


class FeatureButton(QPushButton):
    """Custom feature button for grid"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedSize(187, 70)
        self.setup_button()
        
    def setup_button(self):
        """Setup button appearance and style"""
        if self.title:
            self.setText(self.title)
            self.setStyleSheet("""
                QPushButton {
                    background: #c0c0c0;
                    color: #000000;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'IBM Plex Mono', 'Consolas', monospace;
                    border: none;
                    border-radius: 12px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: #d0d0d0;
                }
                QPushButton:pressed {
                    background: #b0b0b0;
                }
            """)
        else:
            # Empty placeholder card
            self.setEnabled(False)
            self.setStyleSheet("""
                QPushButton {
                    background: #c0c0c0;
                    border: none;
                    border-radius: 12px;
                }
            """)

class MainMenuWindow(QMainWindow):
    """Main menu window with AI features - UI2 exact match"""
    
    def __init__(self):
        super().__init__()
        self.translations = {
            'en': {'title': 'TurnIT - AI Desktop Assistant'},
            'ar': {'title': 'TurnIT - مساعد الذكاء الاصطناعي'},
            'fr': {'title': 'TurnIT - Assistant IA'}
        }
        self.current_language = GlobalSettings().get_language()
        self.init_ui()
        # Connect to global language changes
        GlobalSettings().language_changed.connect(self.on_language_changed)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TurnIT - AI Desktop Assistant")
        self.setFixedSize(781, 535)
        self.center_window()
        
        # Main widget with diagonal gradient background
        main_widget = DiagonalGradientWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sections
        self.create_header(main_layout)
        self.create_center_content(main_layout)
        self.create_footer(main_layout)
    
    def create_header(self, layout):
        """Create header with logo and settings"""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 20, 40, 10)
        
        # Logo section (left)
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(0)
        
        logo_label = QLabel("TurnIT")
        logo_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Gasoek One', 'Arial Black', sans-serif;
                letter-spacing: 0px;
            }
        """)
        logo_layout.addWidget(logo_label)
        
        subtitle_label = QLabel("AI Desktop Assistant")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: 400;
                font-family: 'Alexandria', 'Arial', sans-serif;
                margin-top: -5px;
            }
        """)
        logo_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        
        # Settings icon (right)
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 24px;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        layout.addWidget(header_widget)
    
    def create_center_content(self, layout):
        """Create centered features container"""
        # Add top spacer
        layout.addStretch()
        
        # Features container card
        features_container = QFrame()
        features_container.setFixedSize(680, 340)
        features_container.setStyleSheet("""
            QFrame {
                background: rgba(80, 80, 80, 0.4);
                border-radius: 20px;
            }
        """)
        
        container_layout = QVBoxLayout(features_container)
        container_layout.setContentsMargins(30, 25, 30, 25)
        container_layout.setSpacing(20)
        
        # "Features" header
        features_header = QLabel("Features")
        features_header.setAlignment(Qt.AlignCenter)
        features_header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: 600;
                font-family: 'Alexandria', 'Arial', sans-serif;
                background: rgba(100, 100, 100, 0.3);
                border-radius: 12px;
                padding: 12px;
            }
        """)
        container_layout.addWidget(features_header)
        
        # 3x3 Grid of feature buttons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Row 0: Voice to Text, Text to Voice, Images Analysis
        self.voice_to_text_btn = FeatureButton("Voice to Text")
        self.voice_to_text_btn.clicked.connect(self.open_audio_to_text)
        grid_layout.addWidget(self.voice_to_text_btn, 0, 0)
        
        self.text_to_voice_btn = FeatureButton("Text to Voice")
        self.text_to_voice_btn.clicked.connect(self.open_text_to_speech)
        grid_layout.addWidget(self.text_to_voice_btn, 0, 1)
        
        self.images_analysis_btn = FeatureButton("Images Analysis")
        self.images_analysis_btn.clicked.connect(self.open_image_analysis)
        grid_layout.addWidget(self.images_analysis_btn, 0, 2)
        
        # Row 1: Empty placeholders
        for col in range(3):
            empty_btn = FeatureButton("")
            grid_layout.addWidget(empty_btn, 1, col)
        
        # Row 2: Empty placeholders
        for col in range(3):
            empty_btn = FeatureButton("")
            grid_layout.addWidget(empty_btn, 2, col)
        
        container_layout.addLayout(grid_layout)
        
        # Center the features container
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(features_container)
        center_layout.addStretch()
        
        layout.addLayout(center_layout)
        layout.addStretch()
    
    def create_footer(self, layout):
        """Create footer with version and developer info"""
        footer_widget = QWidget()
        footer_widget.setFixedHeight(40)
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(40, 10, 40, 15)
        
        version_label = QLabel("V 1.0 2024 TurnIT")
        version_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-weight: 400;
                font-family: 'IBM Plex Mono', 'Consolas', monospace;
            }
        """)
        footer_layout.addWidget(version_label)
        
        footer_layout.addStretch()
        
        developer_label = QLabel("Developed by putbullet")
        developer_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-weight: 400;
                font-family: 'IBM Plex Mono', 'Consolas', monospace;
            }
        """)
        footer_layout.addWidget(developer_label)
        
        layout.addWidget(footer_widget)
    
    
    def center_window(self):
        """Center window on screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def show_settings(self):
        """Show settings dialog"""
        try:
            from ui.settings_ui import SettingsWindow
            self.settings_window = SettingsWindow()
            self.settings_window.settings_changed.connect(self.on_settings_changed)
            self.settings_window.show()
            logger.info("Settings window opened")
        except Exception as e:
            logger.error(f"Failed to open settings: {str(e)}")
            self.show_error(f"Failed to open settings: {str(e)}")
    
    def on_settings_changed(self, settings):
        """Handle settings changes"""
        logger.info("Settings updated")
        # Here you can apply settings changes to the main window
        # For example, update language, theme, etc.
    
    def tr(self, key):
        """Translate key to current language"""
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def on_language_changed(self, language):
        """Handle global language change"""
        self.current_language = language
        self.update_ui_language()
        logger.info(f"Language changed to: {language}")
    
    def update_ui_language(self):
        """Update all UI text with current language"""
        self.setWindowTitle(self.tr('title'))
        # Note: Full implementation would recreate/update all labels
        # For now, this is a placeholder for the language update mechanism
    
    def show_error(self, message):
        """Show error message"""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText("An error occurred")
        msg.setInformativeText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec()
        # TODO: Implement settings dialog
    
    def open_audio_to_text(self):
        """Open Audio to Text workflow"""
        try:
            from ui.audio_to_text_ui import AudioToTextWindow
            self.audio_window = AudioToTextWindow()
            self.audio_window.show()
            logger.info("Opened Audio to Text window")
        except ImportError:
            logger.error("Audio to Text UI not found")
            self.show_placeholder("Audio to Text")
    
    def open_text_to_speech(self):
        """Open Text to Speech workflow"""
        try:
            from ui.text_to_speech_ui import TextToSpeechWindow
            self.tts_window = TextToSpeechWindow()
            self.tts_window.show()
            logger.info("Opened Text to Speech window")
        except ImportError:
            logger.error("Text to Speech UI not found")
            self.show_placeholder("Text to Speech")
    
    def open_image_analysis(self):
        """Open Image Analysis workflow"""
        try:
            from ui.image_analysis_ui import ImageAnalysisWindow
            self.image_window = ImageAnalysisWindow()
            self.image_window.show()
            logger.info("Opened Image Analysis window")
        except ImportError:
            logger.error("Image Analysis UI not found")
            self.show_placeholder("Image Analysis")
    
    def show_placeholder(self, feature_name):
        """Show placeholder message for unimplemented features"""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("TurnIT")
        msg.setText(f"{feature_name} feature coming soon!")
        msg.setInformativeText("This feature is currently under development.")
        msg.setStyleSheet("""
            QMessageBox {
                background: #2a2a2a;
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                background: #00d4ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: #00b8e6;
            }
        """)
        msg.exec()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainMenuWindow()
    window.show()
    sys.exit(app.exec())
