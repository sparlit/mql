# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Sovereign Universal Installer (Cross-Platform)

import os
import sys
import subprocess
import json
import shutil

def print_banner():
    print("="*60)
    print("🛰️  AAT V5.0.0: Sovereign Citadel Universal Installer")
    print("="*60)

def check_python():
    print("[*] Checking Python version...")
    if sys.version_info < (3, 10):
        print("[!] Error: Python 3.10+ is required.")
        sys.exit(1)
    print(f"[+] Python {sys.version_info.major}.{sys.version_info.minor} detected.")

def setup_venv():
    print("[*] Setting up virtual environment...")
    if not os.path.exists(".venv"):
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("[+] Virtual environment created.")
    else:
        print("[+] Virtual environment already exists.")

def install_dependencies():
    print("[*] Installing institutional dependencies...")
    pip_exe = os.path.join(".venv", "Scripts", "pip.exe") if os.name == 'nt' else os.path.join(".venv", "bin", "pip")
    subprocess.run([pip_exe, "install", "--upgrade", "pip"], check=True)
    subprocess.run([pip_exe, "install", "-r", "requirements.txt"], check=True)
    print("[+] Dependencies installed successfully.")

def init_vault():
    print("[*] Initializing Sovereign Vault...")
    vault_path = os.path.join("src", "vault.json")
    if not os.path.exists(vault_path):
        default_vault = {
            "MASTER_KEY": "REPLACE_WITH_32_CHAR_SECRET_KEY",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "admin_password_change_me",
            "JWT_SECRET": os.urandom(32).hex()
        }
        with open(vault_path, "w") as f:
            json.dump(default_vault, f, indent=2)
        print(f"[+] Vault created at {vault_path}. PLEASE UPDATE IT!")
    else:
        print("[+] Vault already exists.")

def deploy_mql5():
    print("[*] MQL5 deployment instructions:")
    print("    1. Copy MQL5/Experts/AAT_Sovereign_EA.mq5 to your MT5 Experts folder.")
    print("    2. Copy all files in MQL5/Include/ to your MT5 Include folder.")
    print("[+] MQL5 source files are ready in the root directory.")

def main():
    print_banner()
    check_python()
    setup_venv()
    install_dependencies()
    init_vault()
    deploy_mql5()
    print("\n[✔] Sovereign Citadel installation complete.")
    print("[!] Run the engine with: scripts/run_engine.bat (Windows) or python src/core/main.py (Linux/macOS)")

if __name__ == "__main__":
    main()
