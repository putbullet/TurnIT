"""
Dependency checker for TurnIT
Checks and auto-installs missing packages on startup
"""

import sys
import subprocess
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Required packages with their pip install names
REQUIRED_PACKAGES = {
    'PySide6': 'PySide6',
    'torch': 'torch',
    'transformers': 'transformers',
    'PIL': 'Pillow',
    'cv2': 'opencv-python',
    'numpy': 'numpy',
    'pygame': 'pygame',
    'gtts': 'gtts',
    'pyttsx3': 'pyttsx3',
    'pyaudio': 'pyaudio',
    'sounddevice': 'sounddevice',
    'librosa': 'librosa',
    'soundfile': 'soundfile',
    'easyocr': 'easyocr',
    'matplotlib': 'matplotlib',
    'requests': 'requests',
    'tqdm': 'tqdm'
}

def check_package(package_name: str) -> bool:
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(pip_name: str) -> bool:
    """Install a package using pip"""
    try:
        print(f"Installing {pip_name}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pip_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"✓ {pip_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {pip_name}: {str(e)}")
        return False

def check_and_install_dependencies(silent: bool = False) -> Tuple[bool, List[str]]:
    """
    Check for missing dependencies and install them
    
    Returns:
        Tuple of (all_installed: bool, missing_packages: List[str])
    """
    missing_packages = []
    
    if not silent:
        print("\n" + "="*70)
        print("Checking dependencies...")
        print("="*70 + "\n")
    
    # Check all required packages
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        if not check_package(import_name):
            missing_packages.append(pip_name)
    
    if not missing_packages:
        if not silent:
            print("✓ All dependencies are installed\n")
        return True, []
    
    if not silent:
        print(f"Found {len(missing_packages)} missing packages:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print()
    
    # Ask user if they want to auto-install
    if not silent:
        response = input("Do you want to install missing packages now? (yes/no): ").strip().lower()
        if response != 'yes':
            print("\nPlease install the following packages manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False, missing_packages
        print()
    
    # Install missing packages
    failed_packages = []
    for pip_name in missing_packages:
        if not install_package(pip_name):
            failed_packages.append(pip_name)
    
    if failed_packages:
        print(f"\n✗ Failed to install {len(failed_packages)} packages:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\nPlease install them manually:")
        print(f"pip install {' '.join(failed_packages)}")
        return False, failed_packages
    
    if not silent:
        print("\n" + "="*70)
        print("✓ All dependencies installed successfully!")
        print("="*70 + "\n")
    
    return True, []

def check_critical_dependencies() -> bool:
    """
    Check only critical dependencies (PySide6, numpy, pillow)
    Returns True if all critical deps are available
    """
    critical_packages = ['PySide6', 'numpy', 'PIL']
    
    for pkg in critical_packages:
        if not check_package(pkg):
            return False
    
    return True

if __name__ == "__main__":
    # Test dependency checker
    success, missing = check_and_install_dependencies()
    sys.exit(0 if success else 1)
