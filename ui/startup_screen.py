"""
Startup Screen for TurnIT Application
Shows splash screen, privacy policy agreement, and initial setup
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QCheckBox, QProgressBar,
    QTextEdit, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PySide6.QtGui import QFont, QPixmap, QDesktopServices, QMovie

from ui.main_menu import MainMenu
from ui.setup_dialog import SetupDialog

class StartupScreen(QMainWindow):
    """Startup screen with privacy policy and setup"""
    
    def __init__(self, app_setup):
        super().__init__()
        self.app_setup = app_setup
        self.logger = logging.getLogger(__name__)
        self.main_menu = None
        
        # Setup window
        self.setWindowTitle("TurnIT v1.0 - AI Desktop Application")
        self.setFixedSize(900, 700)
        
        # Center window on screen
        self.center_window()
        
        # Create UI
        self.setup_ui()
        
        # Check if setup is already complete
        QTimer.singleShot(1000, self.check_initial_setup)
    
    def center_window(self):
        """Center the window on the screen"""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())
    
    def setup_ui(self):
        """Setup the startup screen UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 40, 50, 40)
        
        # Title section
        self.create_title_section(main_layout)
        
        # Privacy policy section
        self.create_privacy_section(main_layout)
        
        # Start button section
        self.create_start_section(main_layout)
        
        # Footer section
        self.create_footer_section(main_layout)
    
    def create_title_section(self, layout):
        """Create the title section"""
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main title
        title_label = QLabel("TurnIT")
        title_font = QFont("Arial", 60, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #58a6ff;
                background: linear-gradient(135deg, #58a6ff, #a5b4fc);
                -webkit-background-clip: text;
                background-clip: text;
                text-shadow: 0 0 20px rgba(88, 166, 255, 0.5);
            }
        """)
        
        # Subtitle
        subtitle_label = QLabel("AI-Powered Desktop Application")
        subtitle_font = QFont("Arial", 18)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #7d8590;
                margin-top: 10px;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        layout.addLayout(title_layout)
    
    def create_privacy_section(self, layout):
        """Create privacy policy section"""
        # Privacy policy frame
        privacy_frame = QFrame()
        privacy_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        privacy_frame.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        privacy_layout = QVBoxLayout(privacy_frame)
        
        # Privacy policy header
        privacy_header = QLabel("Privacy Policy & Terms of Use")
        privacy_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        privacy_header.setStyleSheet("color: #e6edf3; margin-bottom: 10px;")
        
        # Privacy policy text
        privacy_text = QTextEdit()
        privacy_text.setFixedHeight(200)
        privacy_text.setReadOnly(True)
        privacy_text.setPlainText("""
TurnIT Privacy Policy & Terms of Use

1. Data Processing: This application processes audio, text, and images locally on your device. No data is transmitted to external servers unless explicitly stated.

2. AI Models: The application downloads and uses open-source AI models for speech recognition, text-to-speech, and image analysis. These models run entirely offline after initial download.

3. Storage: Analysis results and temporary files are stored locally on your device and can be deleted at any time.

4. Network Access: Network access is only required for initial model downloads. After setup, the application runs completely offline.

5. Privacy: Your privacy is important. No personal data is collected, transmitted, or stored remotely.

6. Usage: This software is provided "as-is" for educational and research purposes. Use responsibly and in accordance with local laws.

7. License: This application uses open-source components. See individual license files for details.

By using this application, you agree to these terms and acknowledge that you understand how your data is processed.
        """)
        
        privacy_text.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 6px;
                padding: 15px;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        
        # Checkbox for agreement
        self.privacy_checkbox = QCheckBox("I have read and agree to the Privacy Policy & Terms of Use")
        self.privacy_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e6edf3;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.privacy_checkbox.stateChanged.connect(self.on_privacy_check_changed)
        
        privacy_layout.addWidget(privacy_header)
        privacy_layout.addWidget(privacy_text)
        privacy_layout.addWidget(self.privacy_checkbox)
        
        layout.addWidget(privacy_frame)
    
    def create_start_section(self, layout):
        """Create start button section"""
        start_layout = QHBoxLayout()
        start_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Start button
        self.start_button = QPushButton("START")
        self.start_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.start_button.setFixedSize(200, 60)
        self.start_button.setEnabled(False)  # Disabled until checkbox is checked
        self.start_button.clicked.connect(self.on_start_clicked)
        
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ea043;
                box-shadow: 0 0 15px rgba(35, 134, 54, 0.5);
            }
            QPushButton:disabled {
                background-color: #21262d;
                color: #7d8590;
            }
        """)
        
        start_layout.addWidget(self.start_button)
        layout.addLayout(start_layout)
    
    def create_footer_section(self, layout):
        """Create footer section"""
        footer_layout = QHBoxLayout()
        
        # Version label
        version_label = QLabel("v1.0")
        version_label.setStyleSheet("color: #7d8590; font-size: 12px;")
        
        # Developer link
        developer_label = QLabel('<a href="https://github.com/putbullet" style="color: #58a6ff; text-decoration: none;">developed by putbullet</a>')
        developer_label.setStyleSheet("font-size: 12px;")
        developer_label.linkActivated.connect(self.open_github_link)
        
        footer_layout.addWidget(version_label)
        footer_layout.addStretch()
        footer_layout.addWidget(developer_label)
        
        layout.addLayout(footer_layout)
    
    def on_privacy_check_changed(self, state):
        """Handle privacy checkbox state change"""
        self.start_button.setEnabled(state == Qt.CheckState.Checked.value)
    
    def open_github_link(self, url):
        """Open GitHub profile link"""
        QDesktopServices.openUrl(QUrl(url))
    
    def check_initial_setup(self):
        """Check if initial setup is needed"""
        if self.app_setup.is_setup_complete():
            self.logger.info("Setup already complete")
        else:
            requirements = self.app_setup.get_setup_requirements()
            self.logger.info(f"Setup required: {requirements}")
    
    def on_start_clicked(self):
        """Handle start button click"""
        if not self.app_setup.is_setup_complete():
            # Show setup dialog
            self.show_setup_dialog()
        else:
            # Go directly to main menu
            self.show_main_menu()
    
    def show_setup_dialog(self):
        """Show the setup dialog for downloading models"""
        setup_dialog = SetupDialog(self.app_setup, self)
        setup_dialog.setup_completed.connect(self.on_setup_completed)
        setup_dialog.show()
    
    def on_setup_completed(self):
        """Handle setup completion"""
        self.logger.info("Setup completed successfully")
        self.show_main_menu()
    
    def show_main_menu(self):
        """Show the main menu"""
        self.main_menu = MainMenu(self.app_setup)
        self.main_menu.show()
        self.hide()  # Hide startup screen
