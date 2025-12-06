@echo off
REM Quick script to push TurnIT to GitHub
REM Run this from the TurnIT_code directory

echo.
echo ================================================
echo Pushing TurnIT to GitHub
echo ================================================
echo.

cd /d "%~dp0"

echo Step 1: Committing files...
git commit -m "Initial commit - TurnIT v1.0.0 with bootstrapper system"

echo.
echo Step 2: Adding remote repository...
git remote add origin https://github.com/putbullet/TurnIT.git 2>nul
if errorlevel 1 (
    echo Remote already exists, updating URL...
    git remote set-url origin https://github.com/putbullet/TurnIT.git
)

echo.
echo Step 3: Renaming branch to main...
git branch -M main

echo.
echo Step 4: Pushing to GitHub...
git push -u origin main --force

echo.
echo ================================================
echo Done! Check your repository:
echo https://github.com/putbullet/TurnIT
echo ================================================
echo.
pause
