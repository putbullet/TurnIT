@echo off
REM TurnIT Build Script for Windows
REM This script creates a standalone executable using PyInstaller

echo ========================================
echo TurnIT Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not found in PATH!
    echo Please activate your virtual environment first.
    echo Run: F:\Venv_Stuff\TurnIT_venv\Scripts\activate
    pause
    exit /b 1
)

echo Python environment detected
echo.

echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Step 3: Building executable...
pyinstaller TurnIT.spec --clean --noconfirm

echo.
if exist dist\TurnIT (
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Executable location: dist\TurnIT\TurnIT.exe
    echo.
    echo To create installer, run: build_installer.bat
) else (
    echo ========================================
    echo Build failed! Check error messages above.
    echo ========================================
)

echo.
pause
