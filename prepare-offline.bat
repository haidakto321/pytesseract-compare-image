@echo off
REM ========================================
REM Prepare Offline Installation Package
REM Run this on a PC with internet to download all dependencies
REM ========================================

echo.
echo ========================================
echo  Offline Package Preparation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

echo This script will download all required Python packages
echo for offline installation on other computers.
echo.
pause

REM Create installers directory
if not exist "installers" (
    echo Creating installers directory...
    mkdir installers
)

if not exist "installers\python-packages" (
    echo Creating python-packages directory...
    mkdir installers\python-packages
)

echo.
echo Downloading Python packages...
echo This may take a few minutes (downloading ~100MB)...
echo.

pip download -r requirements.txt -d installers\python-packages

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to download packages!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Download Complete!
echo ========================================
echo.
echo All Python packages have been downloaded to:
echo   installers\python-packages\
echo.
echo Next steps:
echo.
echo 1. Download Tesseract OCR installer:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo    Save it to: installers\tesseract-installer.exe
echo.
echo 2. Copy the entire project folder to other PCs
echo.
echo 3. Run setup.bat on each PC to install everything offline
echo.
echo.

REM List downloaded files
echo Downloaded packages:
dir /b installers\python-packages\*.whl
echo.

REM Check if Tesseract installer exists
if exist "installers\tesseract-installer.exe" (
    echo [OK] Tesseract installer found!
    echo.
    echo Your offline installation package is ready!
    echo You can now copy this entire folder to other PCs.
) else (
    echo [WARNING] Tesseract installer not found!
    echo.
    echo Please download it from:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo Look for: tesseract-ocr-w64-setup-5.x.x.exe
    echo Save it to: installers\tesseract-installer.exe
)

echo.
pause
