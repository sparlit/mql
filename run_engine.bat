@echo off
setlocal
echo ========================================================
echo   AAT SOVEREIGN CITADEL V4.1.2 - ENGINE START
echo ========================================================

:: 1. Check for Virtual Environment
if not exist .venv (
    echo [ERROR] Virtual Environment not found. Run setup_portable_python.bat first.
    pause
    exit /b 1
)

:: 2. Set Environment Variables
set PYTHONPATH=%CD%
echo [INFO] PYTHONPATH set to: %PYTHONPATH%

:: 3. Execute Engine
echo [INFO] Starting Sovereign Citadel Engine...
.venv\Scripts\python Python/V4_1_2/MainEngine.py

pause
