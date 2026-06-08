@echo off
TITLE AAT Sovereign Engine V5.0.0
echo [*] Activating Sovereign Environment...
IF EXIST .venv\Scripts\activate.bat (
    CALL .venv\Scripts\activate.bat
) ELSE (
    echo [!] Warning: .venv not found. Running with system python.
)
SET PYTHONPATH=.
echo [*] Starting Sovereign Citadel...
python src/core/main.py
pause
