"""
Setup Dialog for TurnIT
Shows real-time progress for model downloads and dependency installation
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


class SetupWorker(QThread):
    """Worker thread for running setup tasks"""
    
    progress_update = Signal(str)  # Message updates
    progress_percent = Signal(int)  # Progress percentage
    finished = Signal(bool)  # Success/failure
    
    def __init__(self, app_setup):
        super().__init__()
        self.app_setup = app_setup
    
    def run(self):
        """Run setup tasks"""
        try:
            # Step 1: Check dependencies
            self.progress_update.emit("Checking dependencies...")
            self.progress_percent.emit(10)
            
            if not self.app_setup.check_dependencies():
                self.progress_update.emit("Installing dependencies...")
                self.progress_percent.emit(20)
                
                if not self.app_setup.install_dependencies():
                    self.finished.emit(False)
                    return
            
            self.progress_update.emit("Dependencies OK ✓")
            self.progress_percent.emit(30)
            
            # Step 2: Check models
            self.progress_update.emit("Checking AI models...")
            model_status = self.app_setup.check_models()
            
            models_needed = [k for k, v in model_status.items() if not v]
            
            if models_needed:
                self.progress_update.emit(f"Need to download {len(models_needed)} models...")
                
                # Download each model
                for i, model_key in enumerate(models_needed):
                    model_name = self.app_setup.models_config[model_key]["name"]
                    size_gb = self.app_setup.models_config[model_key]["size_gb"]
                    
                    self.progress_update.emit(f"Downloading {model_key} ({size_gb} GB)...")
                    base_progress = 30 + (i * 60 // len(models_needed))
                    self.progress_percent.emit(base_progress)
                    
                    success = self.app_setup.download_model(
                        model_key,
                        progress_callback=lambda msg: self.progress_update.emit(msg)
                    )
                    
                    if not success:
                        self.progress_update.emit(f"Failed to download {model_key}")
                        self.finished.emit(False)
                        return
                    
                    self.progress_update.emit(f"{model_key} downloaded ✓")
            else:
                self.progress_update.emit("All models already downloaded ✓")
            
            self.progress_percent.emit(90)
            
            # Final check
            self.progress_update.emit("Verifying setup...")
            if self.app_setup.is_setup_complete():
                self.progress_update.emit("Setup complete! ✓")
                self.progress_percent.emit(100)
                self.finished.emit(True)
            else:
                self.progress_update.emit("Setup verification failed")
                self.finished.emit(False)
                
        except Exception as e:
            logger.error(f"Setup error: {str(e)}")
            self.progress_update.emit(f"Error: {str(e)}")
            self.finished.emit(False)


class SetupDialog(QDialog):
    """Dialog for showing setup progress"""
    
    def __init__(self, app_setup, parent=None):
        super().__init__(parent)
        self.app_setup = app_setup
        self.setup_worker = None
        self.setup_success = False
        
        self.init_ui()
        self.start_setup()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("TurnIT Setup")
        self.setFixedSize(600, 400)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Setting up TurnIT")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Downloading AI models and installing dependencies.\n"
            "This may take 5-10 minutes depending on your internet speed."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(desc_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                background: #2a2a2a;
                color: white;
                font-size: 12px;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #6366f1, stop:1 #00d4ff);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.status_text)
        
        # Cancel/Close button
        self.close_button = QPushButton("Cancel")
        self.close_button.setFixedHeight(40)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.on_close_clicked)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: #ff6b6b;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #ff5252;
            }
            QPushButton:disabled {
                background: #555;
                color: #888;
            }
        """)
        layout.addWidget(self.close_button)
        
        # Apply dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background: #2a2a2a;
            }
        """)
    
    def start_setup(self):
        """Start the setup process"""
        self.setup_worker = SetupWorker(self.app_setup)
        self.setup_worker.progress_update.connect(self.on_progress_update)
        self.setup_worker.progress_percent.connect(self.on_progress_percent)
        self.setup_worker.finished.connect(self.on_setup_finished)
        self.setup_worker.start()
    
    def on_progress_update(self, message):
        """Handle progress message update"""
        self.status_text.append(message)
        # Auto-scroll to bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
    
    def on_progress_percent(self, percent):
        """Handle progress percentage update"""
        self.progress_bar.setValue(percent)
    
    def on_setup_finished(self, success):
        """Handle setup completion"""
        self.setup_success = success
        
        if success:
            self.close_button.setText("Continue")
            self.close_button.setStyleSheet("""
                QPushButton {
                    background: #00d4ff;
                    color: #1a1a1a;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background: #00bfea;
                }
            """)
        else:
            self.close_button.setText("Close")
            QMessageBox.critical(
                self,
                "Setup Failed",
                "Setup could not be completed. Please check the logs and try again."
            )
    
    def on_close_clicked(self):
        """Handle close button click"""
        if self.setup_worker and self.setup_worker.isRunning():
            # Setup is running, ask for confirmation
            reply = QMessageBox.question(
                self,
                "Cancel Setup",
                "Setup is in progress. Are you sure you want to cancel?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.setup_worker.terminate()
                self.reject()
        else:
            # Setup finished or not started
            if self.setup_success:
                self.accept()
            else:
                self.reject()
