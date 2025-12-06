#!/usr/bin/env python3
"""
TurnIT Application Bootstrapper
================================
Automatically installs Python, Git, clones the repository, installs dependencies,
and launches the TurnIT application. Designed for non-technical users.

Author: TurnIT Development Team
Version: 1.0.0
Date: December 6, 2025
"""

import os
import sys
import subprocess
import platform
import urllib.request
import shutil
import time
from pathlib import Path

# ============================================================================
# CONFIGURATION - Modify these settings for your project
# ============================================================================

GITHUB_REPO_URL = "https://github.com/putbullet/TurnIT.git"  # Your GitHub repository URL
PROJECT_NAME = "TurnIT"
MAIN_SCRIPT = "main_app.py"  # The main Python script to run
REQUIREMENTS_FILE = "requirements.txt"
MIN_PYTHON_VERSION = (3, 10)  # Minimum Python version required

# Installation directory (default: user's home directory)
DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser("~"), PROJECT_NAME)

# Download URLs for installers
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
GIT_INSTALLER_URL = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_banner():
    """Print a welcome banner."""
    print("\n" + "="*70)
    print(f"  {PROJECT_NAME} Application Bootstrapper")
    print("="*70)
    print("  This tool will automatically set up everything you need.")
    print("  Please wait while we prepare your application...\n")
    print("="*70 + "\n")

def print_step(message):
    """Print a step message with formatting."""
    print(f"\n[STEP] {message}")
    print("-" * 70)

def print_success(message):
    """Print a success message."""
    print(f"[✓] {message}")

def print_error(message):
    """Print an error message."""
    print(f"[✗] ERROR: {message}")

def print_info(message):
    """Print an info message."""
    print(f"[i] {message}")

def is_windows():
    """Check if running on Windows."""
    return platform.system() == "Windows"

def command_exists(command):
    """Check if a command exists in the system PATH."""
    return shutil.which(command) is not None

def run_command(command, shell=True, check=True, capture_output=False):
    """Run a shell command and handle errors."""
    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=shell,
                check=check,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=shell, check=check)
            return None
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        if capture_output and e.stderr:
            print_error(f"Error details: {e.stderr}")
        raise

def download_file(url, destination):
    """Download a file from URL to destination with progress."""
    print_info(f"Downloading from: {url}")
    print_info(f"Saving to: {destination}")
    
    try:
        with urllib.request.urlopen(url) as response, open(destination, 'wb') as out_file:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            block_size = 8192
            
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                    
                downloaded += len(buffer)
                out_file.write(buffer)
                
                # Show progress
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\rProgress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
            
            print()  # New line after progress
            print_success(f"Downloaded successfully: {destination}")
            return True
            
    except Exception as e:
        print_error(f"Download failed: {str(e)}")
        return False

# ============================================================================
# PYTHON INSTALLATION
# ============================================================================

def check_python():
    """Check if Python is installed and meets minimum version requirement."""
    print_step("Checking Python installation...")
    
    if not command_exists("python"):
        print_info("Python is not installed on this system.")
        return False
    
    try:
        # Get Python version
        version_output = run_command("python --version", capture_output=True)
        print_info(f"Found: {version_output}")
        
        # Parse version
        version_parts = version_output.split()[1].split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        if (major, minor) >= MIN_PYTHON_VERSION:
            print_success(f"Python {major}.{minor} meets requirements (>= {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]})")
            return True
        else:
            print_info(f"Python {major}.{minor} is too old. Minimum required: {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}")
            return False
            
    except Exception as e:
        print_error(f"Failed to check Python version: {str(e)}")
        return False

def install_python():
    """Download and install Python silently."""
    print_step("Installing Python...")
    
    if not is_windows():
        print_error("Automatic Python installation is only supported on Windows.")
        print_info("Please install Python manually from: https://www.python.org/downloads/")
        return False
    
    # Create temp directory for installer
    temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'turnit_setup')
    os.makedirs(temp_dir, exist_ok=True)
    
    installer_path = os.path.join(temp_dir, 'python_installer.exe')
    
    # Download Python installer
    print_info("Downloading Python installer...")
    if not download_file(PYTHON_INSTALLER_URL, installer_path):
        return False
    
    # Install Python silently with PATH addition
    print_info("Installing Python (this may take a few minutes)...")
    install_command = f'"{installer_path}" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0'
    
    try:
        run_command(install_command, shell=True, check=True)
        print_success("Python installed successfully!")
        
        # Wait for installation to complete
        time.sleep(5)
        
        # Refresh environment variables
        print_info("Refreshing environment variables...")
        refresh_env()
        
        # Verify installation
        if command_exists("python"):
            print_success("Python is now available in PATH")
            return True
        else:
            print_error("Python was installed but is not in PATH. Please restart this script.")
            return False
            
    except Exception as e:
        print_error(f"Python installation failed: {str(e)}")
        return False
    finally:
        # Cleanup installer
        if os.path.exists(installer_path):
            try:
                os.remove(installer_path)
            except:
                pass

def refresh_env():
    """Refresh environment variables (Windows only)."""
    if is_windows():
        # Update PATH from registry
        import winreg
        try:
            # Read user PATH
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ) as key:
                user_path, _ = winreg.QueryValueEx(key, 'PATH')
            
            # Read system PATH
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_READ) as key:
                system_path, _ = winreg.QueryValueEx(key, 'PATH')
            
            # Update current process PATH
            os.environ['PATH'] = f"{user_path};{system_path}"
            print_success("Environment variables refreshed")
        except Exception as e:
            print_info(f"Could not refresh environment: {str(e)}")

# ============================================================================
# GIT INSTALLATION
# ============================================================================

def check_git():
    """Check if Git is installed."""
    print_step("Checking Git installation...")
    
    if not command_exists("git"):
        print_info("Git is not installed on this system.")
        return False
    
    try:
        version_output = run_command("git --version", capture_output=True)
        print_info(f"Found: {version_output}")
        print_success("Git is installed and available")
        return True
    except Exception as e:
        print_error(f"Failed to check Git version: {str(e)}")
        return False

def install_git():
    """Download and install Git silently."""
    print_step("Installing Git...")
    
    if not is_windows():
        print_error("Automatic Git installation is only supported on Windows.")
        print_info("Please install Git manually from: https://git-scm.com/downloads")
        return False
    
    # Create temp directory for installer
    temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'turnit_setup')
    os.makedirs(temp_dir, exist_ok=True)
    
    installer_path = os.path.join(temp_dir, 'git_installer.exe')
    
    # Download Git installer
    print_info("Downloading Git installer...")
    if not download_file(GIT_INSTALLER_URL, installer_path):
        return False
    
    # Install Git silently
    print_info("Installing Git (this may take a few minutes)...")
    install_command = f'"{installer_path}" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\\reg\\shellhere,assoc,assoc_sh"'
    
    try:
        run_command(install_command, shell=True, check=True)
        print_success("Git installed successfully!")
        
        # Wait for installation to complete
        time.sleep(5)
        
        # Add Git to PATH manually
        git_paths = [
            r"C:\Program Files\Git\cmd",
            r"C:\Program Files\Git\bin",
            r"C:\Program Files (x86)\Git\cmd",
            r"C:\Program Files (x86)\Git\bin"
        ]
        
        for git_path in git_paths:
            if os.path.exists(git_path) and git_path not in os.environ['PATH']:
                os.environ['PATH'] = f"{git_path};{os.environ['PATH']}"
                print_info(f"Added to PATH: {git_path}")
        
        # Verify installation
        if command_exists("git"):
            print_success("Git is now available in PATH")
            return True
        else:
            print_error("Git was installed but is not in PATH. Please restart this script.")
            return False
            
    except Exception as e:
        print_error(f"Git installation failed: {str(e)}")
        return False
    finally:
        # Cleanup installer
        if os.path.exists(installer_path):
            try:
                os.remove(installer_path)
            except:
                pass

# ============================================================================
# REPOSITORY MANAGEMENT
# ============================================================================

def clone_repository(install_dir):
    """Clone the GitHub repository."""
    print_step(f"Cloning repository to: {install_dir}")
    
    # Check if directory already exists
    if os.path.exists(install_dir):
        if os.path.isdir(install_dir) and os.listdir(install_dir):
            print_info("Project directory already exists and is not empty.")
            
            # Check if it's a git repository
            git_dir = os.path.join(install_dir, '.git')
            if os.path.exists(git_dir):
                print_success("Repository is already cloned. Skipping clone step.")
                return True
            else:
                print_info("Directory exists but is not a git repository.")
                response = input("Do you want to delete it and clone fresh? (yes/no): ").strip().lower()
                if response == 'yes':
                    try:
                        shutil.rmtree(install_dir)
                        print_success("Removed existing directory")
                    except Exception as e:
                        print_error(f"Failed to remove directory: {str(e)}")
                        return False
                else:
                    print_info("Using existing directory without cloning.")
                    return True
    
    # Create parent directory if needed
    parent_dir = os.path.dirname(install_dir)
    os.makedirs(parent_dir, exist_ok=True)
    
    # Clone repository
    print_info(f"Cloning from: {GITHUB_REPO_URL}")
    clone_command = f'git clone "{GITHUB_REPO_URL}" "{install_dir}"'
    
    try:
        run_command(clone_command, shell=True, check=True)
        print_success(f"Repository cloned successfully to: {install_dir}")
        return True
    except Exception as e:
        print_error(f"Failed to clone repository: {str(e)}")
        print_info("Please check your internet connection and the repository URL.")
        return False

def update_repository(install_dir):
    """Update the repository if it already exists."""
    print_step("Checking for updates...")
    
    git_dir = os.path.join(install_dir, '.git')
    if not os.path.exists(git_dir):
        print_info("Not a git repository. Skipping update.")
        return True
    
    try:
        original_dir = os.getcwd()
        os.chdir(install_dir)
        
        # Fetch latest changes
        print_info("Fetching latest changes...")
        run_command("git fetch origin", shell=True, check=True)
        
        # Check if updates are available
        status = run_command("git status -uno", shell=True, capture_output=True, check=False)
        
        if "Your branch is behind" in status:
            print_info("Updates are available. Pulling changes...")
            run_command("git pull origin main", shell=True, check=True)
            print_success("Repository updated successfully!")
        else:
            print_success("Repository is already up to date.")
        
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print_info(f"Could not update repository: {str(e)}")
        print_info("Continuing with existing version...")
        try:
            os.chdir(original_dir)
        except:
            pass
        return True

# ============================================================================
# DEPENDENCY MANAGEMENT
# ============================================================================

def upgrade_pip():
    """Upgrade pip to the latest version."""
    print_step("Upgrading pip...")
    
    try:
        run_command("python -m pip install --upgrade pip", shell=True, check=True)
        print_success("pip upgraded successfully!")
        return True
    except Exception as e:
        print_info(f"Could not upgrade pip: {str(e)}")
        print_info("Continuing with current pip version...")
        return True

def install_dependencies(install_dir):
    """Install project dependencies from requirements.txt."""
    print_step("Installing project dependencies...")
    
    requirements_path = os.path.join(install_dir, REQUIREMENTS_FILE)
    
    if not os.path.exists(requirements_path):
        print_info(f"{REQUIREMENTS_FILE} not found. Skipping dependency installation.")
        return True
    
    print_info(f"Reading dependencies from: {requirements_path}")
    print_info("This may take several minutes depending on the number of packages...")
    
    try:
        # Install dependencies
        install_command = f'python -m pip install -r "{requirements_path}"'
        run_command(install_command, shell=True, check=True)
        print_success("All dependencies installed successfully!")
        return True
        
    except Exception as e:
        print_error(f"Failed to install dependencies: {str(e)}")
        print_info("Some dependencies may not have been installed correctly.")
        
        response = input("Do you want to continue anyway? (yes/no): ").strip().lower()
        return response == 'yes'

# ============================================================================
# APPLICATION LAUNCH
# ============================================================================

def launch_application(install_dir):
    """Launch the main application."""
    print_step("Launching application...")
    
    main_script_path = os.path.join(install_dir, MAIN_SCRIPT)
    
    if not os.path.exists(main_script_path):
        print_error(f"Main script not found: {main_script_path}")
        print_info(f"Please ensure {MAIN_SCRIPT} exists in the project directory.")
        return False
    
    print_info(f"Running: {main_script_path}")
    print_success(f"{PROJECT_NAME} is starting...\n")
    print("="*70 + "\n")
    
    try:
        # Change to project directory and run the script
        original_dir = os.getcwd()
        os.chdir(install_dir)
        
        # Run the application (this will block until the app closes)
        subprocess.run(["python", MAIN_SCRIPT], shell=True, check=True)
        
        os.chdir(original_dir)
        return True
        
    except KeyboardInterrupt:
        print("\n" + "="*70)
        print_info("Application stopped by user.")
        return True
    except Exception as e:
        print_error(f"Failed to launch application: {str(e)}")
        try:
            os.chdir(original_dir)
        except:
            pass
        return False

# ============================================================================
# MAIN BOOTSTRAPPER LOGIC
# ============================================================================

def main():
    """Main bootstrapper function - orchestrates all setup steps."""
    
    print_banner()
    
    # Step 1: Check and install Python
    if not check_python():
        if not install_python():
            print_error("Python installation failed. Cannot continue.")
            print_info("Please install Python manually from: https://www.python.org/downloads/")
            input("\nPress Enter to exit...")
            sys.exit(1)
    
    # Step 2: Check and install Git
    if not check_git():
        if not install_git():
            print_error("Git installation failed. Cannot continue.")
            print_info("Please install Git manually from: https://git-scm.com/downloads")
            input("\nPress Enter to exit...")
            sys.exit(1)
    
    # Step 3: Determine installation directory
    print_step("Determining installation location...")
    install_dir = DEFAULT_INSTALL_DIR
    print_info(f"Installation directory: {install_dir}")
    
    # Ask user if they want to change location
    response = input(f"\nUse this location? (yes/no, default: yes): ").strip().lower()
    if response == 'no':
        custom_dir = input("Enter custom installation path: ").strip()
        if custom_dir:
            install_dir = custom_dir
            print_info(f"Using custom location: {install_dir}")
    
    # Step 4: Clone or update repository
    if not clone_repository(install_dir):
        print_error("Repository setup failed. Cannot continue.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Try to update if repository already existed
    update_repository(install_dir)
    
    # Step 5: Upgrade pip
    upgrade_pip()
    
    # Step 6: Install dependencies
    if not install_dependencies(install_dir):
        print_error("Dependency installation failed.")
        response = input("Do you want to try launching the application anyway? (yes/no): ").strip().lower()
        if response != 'yes':
            input("\nPress Enter to exit...")
            sys.exit(1)
    
    # Step 7: Launch application
    print("\n" + "="*70)
    print("  Setup Complete! Launching application...")
    print("="*70)
    
    if not launch_application(install_dir):
        print_error("Application launch failed.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Completion message
    print("\n" + "="*70)
    print(f"  Thank you for using {PROJECT_NAME}!")
    print("="*70)
    print_info(f"Project location: {install_dir}")
    print_info("You can run this bootstrapper again anytime to launch the application.")
    print("\n")
    input("Press Enter to exit...")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print_info("Setup cancelled by user.")
        print("="*70)
        input("\nPress Enter to exit...")
        sys.exit(0)
    except Exception as e:
        print("\n\n" + "="*70)
        print_error(f"Unexpected error: {str(e)}")
        print("="*70)
        print_info("Please report this error to the development team.")
        input("\nPress Enter to exit...")
        sys.exit(1)
