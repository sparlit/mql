@echo off
setlocal
echo ========================================================
echo   AAT SOVEREIGN CITADEL V4.1.2 - PORTABLE SETUP
echo ========================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.10+ not found in PATH.
    pause
    exit /b 1
)

:: 2. Create Virtual Environment
echo [1/3] Creating Virtual Environment (.venv)...
python -m venv .venv

:: 3. Upgrade Pip
echo [2/3] Upgrading Pip...
.venv\Scripts\python -m pip install --upgrade pip

:: 4. Install Institutional Dependencies
echo [3/3] Installing Masterpiece Dependencies...
.venv\Scripts\python -m pip install -r Python/requirements.txt

echo ========================================================
echo   SETUP COMPLETE. USE run_engine.bat TO START.
echo ========================================================
pause
