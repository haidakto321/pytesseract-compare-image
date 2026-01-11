@echo off
REM ========================================
REM Quick Image Comparison Script
REM Usage: compare.bat folder1 folder2
REM Or edit FOLDER1 and FOLDER2 below for defaults
REM ========================================

echo.
echo ========================================
echo  Image Comparison Tool
echo ========================================
echo.

REM Check if arguments were provided
if "%~1"=="" (
    REM No arguments - use default folders
    set FOLDER1=test_images\version1
    set FOLDER2=test_images\version2
    echo Using default folders:
) else (
    REM Arguments provided - use them
    set FOLDER1=%~1
    set FOLDER2=%~2
    echo Using provided folders:
)

REM Check if FOLDER2 was provided
if "%FOLDER2%"=="" (
    echo [ERROR] Please provide two folders!
    echo.
    echo Usage:
    echo   compare.bat folder1 folder2
    echo.
    echo Example:
    echo   compare.bat test_images\version1 test_images\version2
    echo.
    pause
    exit /b 1
)

REM Check if folders exist
if not exist "%FOLDER1%" (
    echo [ERROR] Folder 1 not found: %FOLDER1%
    echo.
    pause
    exit /b 1
)

if not exist "%FOLDER2%" (
    echo [ERROR] Folder 2 not found: %FOLDER2%
    echo.
    pause
    exit /b 1
)

echo   Folder 1: %FOLDER1%
echo   Folder 2: %FOLDER2%
echo.

REM Run comparison
python image_compare.py "%FOLDER1%" "%FOLDER2%"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Comparison failed!
    echo.
    echo Common issues:
    echo   - Python not installed
    echo   - Tesseract OCR not installed
    echo   - Missing Python packages (run setup.bat)
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Comparison Complete!
echo ========================================
echo.
echo Opening HTML report...
start comparison_report.html

echo.
pause
