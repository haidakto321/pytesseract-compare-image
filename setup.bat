@echo off
REM ========================================
REM Image Comparison Tool - Setup Script
REM Windows Offline Installation
REM ========================================

echo.
echo ========================================
echo  Image Comparison Tool Setup
echo ========================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
echo [OK] Python is installed
python --version
echo.

REM Check if Tesseract is installed
echo [2/4] Checking Tesseract OCR installation...
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Tesseract OCR is not installed or not in PATH!
    echo.
    echo Would you like to install Tesseract now?
    echo.
    set /p INSTALL_TESSERACT="Install Tesseract? (y/n): "
    
    if /i "!INSTALL_TESSERACT!"=="y" (
        if exist "installers\tesseract-installer.exe" (
            echo.
            echo Launching Tesseract installer...
            echo Please follow the installation wizard.
            echo.
            echo IMPORTANT: Note the installation path!
            echo You may need to add it to PATH manually.
            echo.
            pause
            start /wait installers\tesseract-installer.exe
            echo.
            echo Tesseract installation completed!
            echo.
            echo Please add Tesseract to your PATH:
            echo 1. Right-click "This PC" - Properties
            echo 2. Advanced system settings - Environment Variables
            echo 3. Edit "Path" under System variables
            echo 4. Add: C:\Program Files\Tesseract-OCR
            echo 5. Click OK and restart this script
            echo.
            pause
            exit /b 0
        ) else (
            echo [ERROR] Tesseract installer not found!
            echo Please download it manually from:
            echo https://github.com/UB-Mannheim/tesseract/wiki
            echo.
            echo Save it to: installers\tesseract-installer.exe
            echo Then run this setup script again.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo [WARNING] Skipping Tesseract installation.
        echo The tool will not work without Tesseract OCR!
        echo.
    )
) else (
    echo [OK] Tesseract OCR is installed
    tesseract --version
)
echo.

REM Install Python packages
echo [3/4] Installing Python packages...
echo.

REM Determine which pip command to use
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    set PIP_CMD=pip
    echo Using pip command: pip
) else (
    echo pip not found in PATH, trying python -m pip...
    python -m pip --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PIP_CMD=python -m pip
        echo Using pip command: python -m pip
    ) else (
        echo.
        echo [ERROR] pip is not available!
        echo.
        echo This usually means pip was not installed with Python.
        echo.
        echo To fix this:
        echo 1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py
        echo 2. Run: python get-pip.py
        echo 3. Run this setup script again
        echo.
        echo Or reinstall Python and make sure to include pip.
        echo.
        pause
        exit /b 1
    )
)
echo.

REM Check if offline packages exist
if exist "installers\python-packages" (
    echo Installing from local packages offline mode
    %PIP_CMD% install --no-index --find-links=installers\python-packages opencv-python numpy Pillow pytesseract python-docx
    if errorlevel 1 (
        echo.
        echo [WARNING] Failed to install packages from local folder!
        echo Trying online installation instead...
        echo.
        %PIP_CMD% install opencv-python numpy Pillow pytesseract python-docx
    )
) else (
    echo Local packages not found, installing from internet...
    %PIP_CMD% install opencv-python numpy Pillow pytesseract python-docx
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install Python packages!
    echo.
    echo Please check:
    echo - Internet connection if installing online
    echo - Disk space if installing from local packages
    echo - Run Command Prompt as Administrator
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] All Python packages installed successfully
echo.

REM Verify installation
echo [4/4] Verifying installation...
python -c "import cv2, numpy, PIL, pytesseract; print('[OK] All modules imported successfully')"
if errorlevel 1 (
    echo [ERROR] Some Python packages are not working correctly!
    pause
    exit /b 1
)
echo.

REM Test the tool
echo ========================================
echo  Testing the tool...
echo ========================================
echo.
python image_compare.py --help
if errorlevel 1 (
    echo.
    echo [WARNING] Tool test failed!
    echo Please check the error messages above.
    echo.
) else (
    echo.
    echo ========================================
    echo  Setup Complete! 
    echo ========================================
    echo.
    echo The Image Comparison Tool is ready to use!
    echo.
    echo Usage:
    echo   python image_compare.py folder1 folder2
    echo.
    echo Or use the quick script:
    echo   compare.bat folder1 folder2
    echo.
    echo Example:
    echo   compare.bat test_images\version1 test_images\version2
    echo.
    echo See README.md for full documentation.
    echo.
)

pause
