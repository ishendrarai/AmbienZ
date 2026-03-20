@echo off
REM ============================================================
REM  AmbieZ — One-click EXE builder for Windows
REM  Run this script in the same folder as AmbieZ.py
REM ============================================================

echo [1/4] Checking Python...
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause & exit /b 1
)

echo [2/4] Installing dependencies...
pip install pyinstaller PySide6 opencv-python-headless numpy mss

echo [3/4] Building EXE (this may take 1-3 minutes)...
pyinstaller AmbieZ.spec --clean --noconfirm

echo [4/4] Done!
IF EXIST "dist\AmbieZ.exe" (
    echo.
    echo  SUCCESS: dist\AmbieZ.exe is ready!
    echo  Copy it anywhere and run — no Python needed.
) ELSE (
    echo  Something went wrong. Check the output above for errors.
)

pause
