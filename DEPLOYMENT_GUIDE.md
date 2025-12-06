# TurnIT Deployment Guide

This guide explains how to build and deploy TurnIT as a standalone Windows application.

## Prerequisites

1. **Python Environment**: Ensure you have the virtual environment at `F:\Venv_Stuff\TurnIT_venv` activated
2. **All Dependencies**: Install all requirements from `requirements_production.txt`
3. **PyInstaller**: Install with `pip install pyinstaller`

## Building the Executable

### Step 1: Activate Virtual Environment
```powershell
F:\Venv_Stuff\TurnIT_venv\Scripts\activate
```

### Step 2: Run Build Script
```powershell
.\build.bat
```

This will:
- Install PyInstaller if needed
- Clean previous builds
- Create a standalone executable in `dist\TurnIT\`
- Include all necessary files and dependencies

### Step 3: Test the Build
Navigate to `dist\TurnIT\` and run `TurnIT.exe` to verify it works correctly.

## Manual Build (Alternative)

If the batch script doesn't work, you can build manually:

```powershell
# Clean previous builds
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build with PyInstaller
pyinstaller TurnIT.spec --clean --noconfirm
```

## Distribution

### Creating a ZIP Package

```powershell
# Navigate to dist folder
cd dist

# Create ZIP archive
Compress-Archive -Path TurnIT -DestinationPath TurnIT-v1.0.0-Windows.zip
```

### Files to Include in Distribution
- `TurnIT.exe` - Main executable
- All DLLs and dependencies in the same folder
- `config/` folder
- `README.md`
- `LICENSE.txt`
- `VERSION.txt`

### Creating an Installer (Optional)

For a professional installer, you can use:
- **Inno Setup** (free, recommended)
- **NSIS** (free)
- **Advanced Installer** (free/paid)

## Deployment Checklist

- [ ] Test on clean Windows machine without Python installed
- [ ] Verify all AI models download correctly on first run
- [ ] Test audio recording with different microphones
- [ ] Test TTS with all voices
- [ ] Test image analysis with various image formats
- [ ] Check all UI elements and language switching
- [ ] Verify settings persistence
- [ ] Test error handling and logging
- [ ] Check application startup time
- [ ] Verify proper cleanup on exit

## Upload to Distribution Platform

### Option 1: GitHub Releases
1. Create a new release on GitHub
2. Upload the ZIP file as a release asset
3. Write release notes from CHANGELOG.md
4. Tag the release with version number (v1.0.0)

### Option 2: Direct Download
1. Upload to your web hosting
2. Provide direct download link
3. Include checksums for verification

## File Size Expectations

- Executable (compressed): ~50-100 MB
- First launch (with models): +2 GB (downloaded automatically)
- Total installed size: ~2.5 GB

## System Requirements to Document

**Minimum:**
- Windows 10/11 (64-bit)
- 4 GB RAM
- 2 GB free disk space
- Dual-core CPU

**Recommended:**
- 8 GB+ RAM
- 5 GB free disk space
- Quad-core CPU
- SSD for faster model loading

## Known Issues

1. **First Launch**: Initial model download takes 5-30 minutes depending on internet speed
2. **Antivirus**: Some antivirus may flag the executable (false positive) - consider code signing
3. **GPU**: CUDA support not included in basic build - CPU only
4. **Symlinks**: Windows symlink warning for HuggingFace cache (can be ignored)

## Code Signing (Recommended)

For production release, consider code signing to avoid Windows SmartScreen warnings:

1. Purchase code signing certificate
2. Sign the executable:
   ```powershell
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com TurnIT.exe
   ```

## Post-Deployment

1. Monitor user feedback and error reports
2. Check logs for common issues
3. Plan updates and bug fixes
4. Update documentation based on user questions
5. Consider telemetry for crash reporting (optional, privacy-respecting)

## Version Updates

When releasing a new version:
1. Update `VERSION.txt`
2. Update `version_info.txt`
3. Update `CHANGELOG.md`
4. Rebuild executable
5. Test thoroughly
6. Create new release package
7. Upload with version tag
