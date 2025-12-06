"""
Setup script for TurnIT Application
Installs dependencies and prepares the application for first run
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main setup function"""
    print("🚀 TurnIT Setup - Installing Dependencies")
    print("=" * 50)
    
    # Essential packages for basic functionality
    essential_packages = [
        "PySide6>=6.5.0",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
        "requests>=2.31.0"
    ]
    
    print("Installing essential packages...")
    for package in essential_packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
    
    print()
    print("🎉 Basic setup complete!")
    print()
    print("To install full AI capabilities, run:")
    print("pip install -r requirements_full.txt")
    print()
    print("To start TurnIT, run:")
    print("python main_app.py")

if __name__ == "__main__":
    main()
