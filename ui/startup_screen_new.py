"""
TurnIT Startup Screen - Exact UI Match
Modern startup interface with smooth diagonal gradient background
"""

import sys
from pathlib import Path

# Import PySide6 components
try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QCheckBox, QMessageBox
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QFont, QPainterPath
except ImportError:
    print("PySide6 not installed. Installing...")
    sys.exit(1)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


class CustomCheckBox(QCheckBox):
    """Custom checkbox with checkmark icon"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(18, 18)
    
    def paintEvent(self, event):
        """Custom paint with checkmark"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw checkbox border and background
        rect = self.rect().adjusted(0, 0, -1, -1)
        
        if self.isChecked():
            # Checked state - purple background
            painter.setBrush(QColor("#6366f1"))
            painter.setPen(QPen(QColor("#6366f1"), 1))
        else:
            # Unchecked state - transparent with border
            painter.setBrush(Qt.transparent)
            painter.setPen(QPen(QColor("#b0b0b0"), 1))
        
        painter.drawRoundedRect(rect, 3, 3)
        
        # Draw checkmark if checked
        if self.isChecked():
            painter.setPen(QPen(QColor("white"), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            # Draw checkmark path
            painter.drawLine(4, 9, 7, 13)
            painter.drawLine(7, 13, 14, 5)
        
        painter.end()


class DiagonalGridWidget(QWidget):
    """Widget with smooth diagonal gradient background"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paintEvent(self, event):
        """Paint smooth diagonal gradient"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create diagonal gradient from top-left to bottom-right
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#252020"))  # Darker at top-left
        gradient.setColorAt(1, QColor("#332B2B"))  # Lighter/reddish-brown at bottom-right
        
        painter.fillRect(self.rect(), gradient)
        painter.end()


class StartupScreenNew(QMainWindow):
    """Modern startup screen for TurnIT with exact UI match"""
    
    def __init__(self, app_setup):
        super().__init__()
        self.app_setup = app_setup
        self.main_menu = None
        
        self.init_ui()
        self.center_window()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("TurnIT")
        self.setFixedSize(640, 650)
        
        # Main widget with smooth diagonal gradient background
        main_widget = DiagonalGridWidget()
        self.setCentralWidget(main_widget)
        
        # Main vertical layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(60, 80, 60, 24)
        main_layout.setSpacing(0)
        
        # Content container (centered)
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(0)
        
        # Logo "TurnIT"
        logo_label = QLabel("TurnIT")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 76px;
                font-weight: 900;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: -2px;
                margin-bottom: 0px;
            }
        """)
        content_layout.addWidget(logo_label)
        content_layout.addSpacing(10)
        
        # Subtitle "AI Desktop Assistant"
        subtitle_label = QLabel("AI Desktop Assistant")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 15px;
                font-weight: 400;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        content_layout.addWidget(subtitle_label)
        content_layout.addSpacing(70)
        
        # Quote text
        quote_label = QLabel(
            '"Time is your most valuable asset. Harness it,\n'
            'prioritize what truly matters, and let your\n'
            'assistant help with everything else"'
        )
        quote_label.setAlignment(Qt.AlignCenter)
        quote_label.setWordWrap(True)
        quote_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 17px;
                font-weight: 400;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.7;
            }
        """)
        content_layout.addWidget(quote_label)
        content_layout.addSpacing(70)
        
        # "Start Here" button
        self.start_button = QPushButton("Start Here")
        self.start_button.setFixedSize(270, 58)
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setStyleSheet("""
            QPushButton {
                background: #b8b8b8;
                color: #2a2a2a;
                font-size: 23px;
                font-weight: 700;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 29px;
            }
            QPushButton:hover {
                background: #c8c8c8;
            }
            QPushButton:pressed {
                background: #a8a8a8;
            }
            QPushButton:disabled {
                background: #808080;
                color: #555555;
            }
        """)
        self.start_button.clicked.connect(self.on_start_clicked)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()
        content_layout.addLayout(button_layout)
        content_layout.addSpacing(18)
        
        # Checkbox with terms agreement
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setAlignment(Qt.AlignCenter)
        
        self.terms_checkbox = CustomCheckBox()
        self.terms_checkbox.stateChanged.connect(self.on_checkbox_changed)
        checkbox_layout.addWidget(self.terms_checkbox)
        
        terms_label = QLabel(
            'I have read and agree to the <a href="#terms" style="color: #b0b0b0; text-decoration: underline;">Terms of Service</a> '
            'and <a href="#privacy" style="color: #b0b0b0; text-decoration: underline;">Privacy Policy</a>'
        )
        terms_label.setOpenExternalLinks(False)
        terms_label.linkActivated.connect(self.on_terms_clicked)
        terms_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 12px;
                font-weight: 400;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        checkbox_layout.addWidget(terms_label)
        
        content_layout.addLayout(checkbox_layout)
        
        # Add content to main layout
        main_layout.addLayout(content_layout)
        main_layout.addStretch()
        
        # Footer with version and developer info
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        version_label = QLabel("V 1.0 2024 TurnIT")
        version_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                font-weight: 400;
                font-family: 'Segoe UI', Arial, sans-serif;
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
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        footer_layout.addWidget(developer_label)
        
        main_layout.addLayout(footer_layout)
        
        # Initially disable start button until checkbox is checked
        self.start_button.setEnabled(False)
    
    def on_checkbox_changed(self, state):
        """Handle checkbox state change"""
        # state is Qt.Checked (2) when checked, Qt.Unchecked (0) when unchecked
        is_checked = (state == Qt.Checked.value) or (state == 2)
        self.start_button.setEnabled(is_checked)
        logger.info(f"Checkbox state changed: {state}, button enabled: {is_checked}")
    
    def on_terms_clicked(self, link):
        """Handle terms/privacy link click"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Terms & Privacy")
        msg.setIcon(QMessageBox.Information)
        
        msg.setText("Terms of Service & Privacy Policy")
        msg.setInformativeText(
            "TurnIT Privacy Policy:\n\n"
            "• All processing happens locally on your device\n"
            "• No data is sent to external servers\n"
            "• AI models run completely offline\n"
            "• Your audio, text, and images stay private\n"
            "• No personal information is collected or transmitted\n"
            "• You can delete all data at any time\n\n"
            "By using TurnIT, you agree to use the software as-is.\n"
            "The developer is not responsible for any issues that may arise."
        )
        
        msg.setStyleSheet("""
            QMessageBox {
                background: #2a2a2a;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QPushButton {
                background: #00d4ff;
                color: #1a1a1a;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00bfea;
            }
        """)
        msg.exec()
    
    def on_start_clicked(self):
        """Handle start button click"""
        try:
            logger.info("Starting TurnIT application...")
            
            # Check if first-time setup is needed
            cache_dir = Path(__file__).parent.parent / "cache"
            setup_status_file = cache_dir / "setup_status.json"
            
            if not setup_status_file.exists():
                # First time setup - show setup screen
                logger.info("First time setup detected")
                self.show_setup_screen()
            else:
                # Setup already complete - show main menu
                logger.info("Setup already complete, showing main menu")
                self.show_main_menu()
                
        except Exception as e:
            logger.error(f"Error starting application: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start application:\n{str(e)}"
            )
    
    def show_setup_screen(self):
        """Show setup/installation screen"""
        # For now, just show main menu (setup can be added later)
        msg = QMessageBox(self)
        msg.setWindowTitle("First Time Setup")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Welcome to TurnIT!")
        msg.setInformativeText(
            "First-time setup will download AI models (~2GB).\n\n"
            "This only happens once and enables:\n"
            "• Speech recognition\n"
            "• Text-to-speech\n"
            "• Image analysis\n\n"
            "Do you want to continue?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox {
                background: #2a2a2a;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QPushButton {
                background: #00d4ff;
                color: #1a1a1a;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #00bfea;
            }
        """)
        
        result = msg.exec()
        
        if result == QMessageBox.Yes:
            # Mark setup as complete and show main menu
            cache_dir = Path(__file__).parent.parent / "cache"
            cache_dir.mkdir(exist_ok=True)
            setup_status_file = cache_dir / "setup_status.json"
            
            import json
            with open(setup_status_file, 'w') as f:
                json.dump({"setup_complete": True}, f)
            
            self.show_main_menu()
    
    def show_main_menu(self):
        """Show main menu window"""
        try:
            from ui.main_menu import MainMenuWindow
            self.main_menu = MainMenuWindow()
            self.main_menu.show()
            self.close()
            logger.info("Main menu opened successfully")
        except Exception as e:
            logger.error(f"Failed to open main menu: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open main menu:\n{str(e)}"
            )
    
    def center_window(self):
        """Center window on screen"""
        try:
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
        except:
            pass

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Mock app setup for testing
    class MockAppSetup:
        def cleanup(self):
            pass
    
    window = StartupScreenNew(MockAppSetup())
    window.show()
    sys.exit(app.exec())
