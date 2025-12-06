@echo off
REM ============================================================================
REM TurnIT Bootstrapper Build Script
REM ============================================================================
REM This script compiles bootstrapper.py into a standalone executable
REM that can be distributed to end users.
REM ============================================================================

echo.
echo ================================================
echo TurnIT Bootstrapper Builder
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if PyInstaller is available
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller is not installed
    echo [INFO] Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo [OK] PyInstaller installed successfully
) else (
    echo [OK] PyInstaller is installed
)

echo.
echo ================================================
echo Cleaning previous builds...
echo ================================================
echo.

if exist build (
    echo Removing build directory...
    rmdir /s /q build
)

if exist dist (
    echo Removing dist directory...
    rmdir /s /q dist
)

if exist TurnIT-Setup.spec (
    echo Removing old spec file...
    del TurnIT-Setup.spec
)

echo [OK] Cleanup complete
echo.

echo ================================================
echo Building executable...
echo ================================================
echo.
echo This may take a few minutes...
echo.

REM Build the bootstrapper
pyinstaller --onefile ^
    --name="TurnIT-Setup" ^
    --clean ^
    --noconfirm ^
    --noupx ^
    bootstrapper.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build Complete!
echo ================================================
echo.
echo Executable location: dist\TurnIT-Setup.exe
echo.

REM Check if executable was created
if exist dist\TurnIT-Setup.exe (
    echo [OK] TurnIT-Setup.exe created successfully
    echo.
    
    REM Get file size
    for %%A in (dist\TurnIT-Setup.exe) do (
        set size=%%~zA
    )
    
    echo File size: %size% bytes
    echo.
    echo You can now distribute dist\TurnIT-Setup.exe to users.
    echo Users simply double-click it to install and run TurnIT.
    echo.
) else (
    echo [ERROR] Executable was not created!
    echo Please check the PyInstaller output above for errors.
    echo.
)

echo ================================================
pause
