"""
Main application entry point for TurnIT
Handles application initialization, setup, and startup flow
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Check and install critical dependencies first
print("TurnIT - Checking dependencies...")
try:
    from utils.dependency_checker import check_critical_dependencies, check_and_install_dependencies
    
    if not check_critical_dependencies():
        print("\n" + "="*70)
        print("MISSING CRITICAL DEPENDENCIES")
        print("="*70)
        print("\nSome required packages are missing.")
        print("Attempting to install them automatically...\n")
        
        success, missing = check_and_install_dependencies()
        
        if not success:
            print("\n" + "="*70)
            print("INSTALLATION FAILED")
            print("="*70)
            print("\nPlease install the missing packages manually:")
            print(f"pip install {' '.join(missing)}")
            print("\nOr install all requirements:")
            print("pip install -r requirements.txt")
            print("\n")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("\nRestarting application with new dependencies...")
        print("="*70 + "\n")

except ImportError as e:
    print(f"Error checking dependencies: {str(e)}")
    print("Please ensure you have installed the requirements:")
    print("pip install -r requirements.txt")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Import PySide6 components
try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
except ImportError:
    print("PySide6 not installed. Please run: pip install PySide6")
    sys.exit(1)

# Import application components
from utils.logger import setup_logging, get_logger
from utils.app_setup import AppSetup
from ui.startup_screen_new import StartupScreenNew

# Setup logging
setup_logging()
logger = get_logger(__name__)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler for uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default handler for keyboard interrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Show error dialog
    error_msg = f"An unexpected error occurred:\\n\\n{exc_type.__name__}: {exc_value}"
    QMessageBox.critical(None, "Critical Error", error_msg)

# Set global exception handler
sys.excepthook = global_exception_handler

class TurnITApplication:
    """Main TurnIT application class"""
    
    def __init__(self):
        self.app = None
        self.app_setup = None
        self.startup_screen = None
        
        # Application constants
        self.app_name = "TurnIT"
        self.app_version = "1.0.0"
        self.app_author = "putbullet"
        self.app_description = "AI-Powered Desktop Application"
    
    def initialize(self):
        """Initialize the application"""
        try:
            logger.info(f"Initializing {self.app_name} v{self.app_version}")
            
            # Create QApplication
            self.app = QApplication(sys.argv)
            self.app.setApplicationName(self.app_name)
            self.app.setApplicationVersion(self.app_version)
            self.app.setOrganizationName(self.app_author)
            
            # Set application icon if available
            icon_path = current_dir / "assets" / "icon.ico"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
            
            # High DPI scaling is now enabled by default in PySide6
            # self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Deprecated
            # self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)     # Deprecated
            
            # Initialize app setup
            self.app_setup = AppSetup()
            
            # Create startup screen
            self.startup_screen = StartupScreenNew(self.app_setup)
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}")
            self.show_error("Initialization Error", f"Failed to initialize application:\\n{str(e)}")
            return False
    
    def show_error(self, title, message):
        """Show error message box"""
        if self.app:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(title)
            msg.setText("An error occurred")
            msg.setInformativeText(message)
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
        else:
            print(f"ERROR - {title}: {message}")
    
    def run(self):
        """Run the application"""
        if not self.initialize():
            return 1
        
        try:
            # Show startup screen
            self.startup_screen.show()
            
            # Start event loop
            return self.app.exec()
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            return 0
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            self.show_error("Application Error", str(e))
            return 1
    
    def cleanup(self):
        """Cleanup application resources"""
        try:
            if self.app_setup:
                self.app_setup.cleanup()
            
            logger.info("Application cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

def main():
    """Main entry point"""
    # Create and run application
    turnit_app = TurnITApplication()
    
    try:
        exit_code = turnit_app.run()
        return exit_code
        
    finally:
        turnit_app.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
