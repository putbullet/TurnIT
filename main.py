#!/usr/bin/env python3
"""
TurnIT v1.0
A fully functional offline AI desktop application

Developer: putbullet
GitHub: https://github.com/putbullet

This application provides AI-powered features including:
- Audio to Text (Speech Recognition)
- Text to Speech
- Image Feature Extraction

All AI models are automatically downloaded and cached on first run
for complete offline functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase

from ui.startup_screen import StartupScreen
from utils.app_setup import AppSetup
from utils.logger import setup_logging

class TurnITApp:
    """Main TurnIT Application Controller"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("TurnIT")
        self.app.setApplicationVersion("1.0")
        self.app.setOrganizationName("putbullet")
        
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Set application-wide dark theme
        self.setup_theme()
        
        # Initialize app setup utility
        self.app_setup = AppSetup()
        
        # Initialize startup screen
        self.startup_screen = None
        
    def setup_theme(self):
        """Setup dark theme and futuristic styling"""
        dark_style = """
        QApplication {
            background-color: #0d1117;
            color: #e6edf3;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        
        QMainWindow {
            background-color: #0d1117;
        }
        
        QWidget {
            background-color: #0d1117;
            color: #e6edf3;
        }
        
        QPushButton {
            background-color: #21262d;
            border: 2px solid #30363d;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            color: #e6edf3;
        }
        
        QPushButton:hover {
            background-color: #30363d;
            border-color: #58a6ff;
            box-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
        }
        
        QPushButton:pressed {
            background-color: #1c2128;
        }
        
        QPushButton:disabled {
            background-color: #161b22;
            border-color: #21262d;
            color: #7d8590;
        }
        
        QLabel {
            color: #e6edf3;
            background: transparent;
        }
        
        QCheckBox {
            color: #e6edf3;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #30363d;
            border-radius: 4px;
            background-color: #21262d;
        }
        
        QCheckBox::indicator:hover {
            border-color: #58a6ff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #238636;
            border-color: #238636;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC4yOCAwLjI4TDMuNzYgNi44TDEuNzIgNC43NkMxLjMyIDQuMzYgMC42OCA0LjM2IDAuMjggNC43NkMtMC4xMiA1LjE2IC0wLjEyIDUuOCAwLjI4IDYuMkwyLjc2IDguNjhDMy4xNiA5LjA4IDMuOCA5LjA4IDQuMiA4LjY4TDExLjcyIDEuMTZDMTIuMTIgMC43NiAxMi4xMiAwLjEyIDExLjcyIC0wLjI4QzExLjMyIC0wLjY4IDEwLjY4IC0wLjY4IDEwLjI4IDAuMjhaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K);
        }
        
        QComboBox {
            background-color: #21262d;
            border: 2px solid #30363d;
            border-radius: 6px;
            padding: 8px 12px;
            min-width: 120px;
        }
        
        QComboBox:hover {
            border-color: #58a6ff;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iNiIgdmlld0JveD0iMCAwIDEwIDYiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNSA1TDkgMSIgc3Ryb2tlPSIjZTZlZGYzIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }
        
        QComboBox QAbstractItemView {
            background-color: #21262d;
            border: 1px solid #30363d;
            selection-background-color: #58a6ff;
        }
        
        QTextEdit, QPlainTextEdit {
            background-color: #0d1117;
            border: 2px solid #30363d;
            border-radius: 6px;
            padding: 12px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #58a6ff;
        }
        
        QProgressBar {
            background-color: #21262d;
            border: 1px solid #30363d;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #238636;
            border-radius: 3px;
        }
        """
        
        self.app.setStyleSheet(dark_style)
        
    def run(self):
        """Run the application"""
        try:
            self.logger.info("Starting TurnIT application...")
            
            # Create and show startup screen
            self.startup_screen = StartupScreen(self.app_setup)
            self.startup_screen.show()
            
            # Run the application
            sys.exit(self.app.exec())
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            sys.exit(1)

def main():
    """Application entry point"""
    try:
        app = TurnITApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
