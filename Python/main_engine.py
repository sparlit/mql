import socket
import json
import threading
import logging
import time
import os
import sqlite3
import base64
from datetime import datetime
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from strategy_master import StrategyMaster
from risk_manager import RiskManager
from data_ingestor import DataIngestor
from vault_manager import VaultManager

# Ensure log directory exists before basicConfig
os.makedirs("Python/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("Python/logs/engine_debug.log"), logging.StreamHandler()]
)

class AutonomousBrain:
    def __init__(self, host='127.0.0.1', port=5555):
        """
        Initialize the AutonomousBrain, prepare crypto keys, subsystems, and the monthly trades database.
        
        Parameters:
        	host (str): Host address the engine will bind to (default '127.0.0.1').
        	port (int): TCP port the engine will listen on (default 5555).
        
        Notes:
        	- Creates a VaultManager and ensures a communication key exists in the vault.
        	- Instantiates StrategyMaster, RiskManager, and DataIngestor components.
        	- Sets up a static AES key and IV used by this stub implementation.
        	- Marks the server active and initializes a SQLite database at `Python/db/trades_YYYYmm.db`.
        """
        self.host = host
        self.port = port
        self.vault = VaultManager()
        self._ensure_keys()

        # Use a hardcoded key for the zero-stub/CI proof of concept to avoid persistence race conditions
        self.key = b"Static32ByteKeyForZeroStubPolicy"
        self.iv = b"Static16ByteIV!!"

        self.strategy_master = StrategyMaster()
        self.risk_manager = RiskManager()
        self.data_ingestor = DataIngestor()
        self.active = True
        self.db_path = f"Python/db/trades_{datetime.now().strftime('%Y%m')}.db"
        self._init_db()

    def _ensure_keys(self):
        """
        Ensure a persisted communication key exists in the vault.
        
        If the vault has no secret named "COMM_KEY", generate a new 32-byte random key, base64-encode it, and store it under "COMM_KEY".
        """
        if not self.vault.get_secret("COMM_KEY"):
            new_key = os.urandom(32)
            self.vault.store_secret("COMM_KEY", base64.b64encode(new_key).decode())

    def _init_db(self):
        """
        Ensure the database directory exists and initialize the monthly SQLite database with the `signals` table.
        
        Creates the directory Python/db if missing and opens the SQLite database at self.db_path. Ensures a table named `signals` exists with columns: `timestamp` (TEXT), `symbol` (TEXT), `signal` (TEXT), `confidence` (INT), `regime` (TEXT), and `verified` (INT).
        """
        os.makedirs("Python/db", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS signals
                        (timestamp TEXT, symbol TEXT, signal TEXT, confidence INT, regime TEXT, verified INT)''')
        conn.commit()
        conn.close()

    def decrypt(self, encrypted_b64):
        """
        Decrypt a base64-encoded AES-CBC ciphertext and return the resulting plaintext.
        
        Parameters:
            encrypted_b64 (str): Base64-encoded ciphertext produced by AES-CBC encryption.
        
        Returns:
            str: Decrypted UTF-8 text with trailing nulls and common PKCS7-like padding bytes removed; invalid UTF-8 bytes are ignored during decoding.
        """
        raw = base64.b64decode(encrypted_b64)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(raw) + decryptor.finalize()
        # Clean potential PKCS7 padding or nulls
        return padded_data.decode('utf-8', errors='ignore').split('\x00')[0].rstrip('\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10')

    def encrypt(self, plaintext):
        """
        Encrypt a UTF-8 plaintext string with the instance AES-CBC key and IV.
        
        Parameters:
            plaintext (str): The plaintext to encrypt (interpreted as UTF-8).
        
        Returns:
            str: Base64-encoded ciphertext produced from encrypting the plaintext with the instance's AES-CBC key and IV.
        """
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(encrypted).decode('utf-8')

    def handle_client(self, conn, addr):
        """
        Handle a single client connection: process an encrypted request for a trading symbol, compute signals, persist the result, and return an encrypted response.
        
        This method reads an encrypted payload from `conn`, decrypts and parses it as JSON to obtain a `symbol`, fetches required market/sentiment/news data, derives a consensus trading `signal`, `confidence`, `regime`, and related timeframe results, and records the signal to the engine database. It sends back an encrypted JSON response containing status, symbol, signal, confidence (as an integer), regime, verification flag, a high-impact-news flag, a timestamp, and any timeframe results. Any exceptions are logged and the connection is closed.
        
        Parameters:
        	conn (socket.socket): Established client socket; method reads from and writes to this connection and ensures it is closed on exit.
        	addr (tuple): Client address tuple (host, port) used for logging context.
        """
        with conn:
            try:
                conn.settimeout(15.0)
                data_raw = conn.recv(16384).decode('utf-8')
                if not data_raw: return

                decrypted_data = self.decrypt(data_raw)
                request = json.loads(decrypted_data)

                symbol = request.get("symbol")
                logging.info(f"Processing {symbol} from {addr}")

                bundle = self.data_ingestor.fetch_all_data(symbol)
                dfs = bundle["prices"]
                sentiment = bundle["sentiment"]
                news = bundle["news"]

                signal, confidence, tf_results = self.strategy_master.get_consensus_signal(dfs, sentiment)
                regime = self.risk_manager.evaluate_market_regime(dfs.get('H1'))

                has_news = any(item['impact'] == 'high' for item in news[:5])
                verified = self.strategy_master.verify_trade(dfs, signal, confidence)

                response = {
                    "status": "success", "symbol": symbol, "signal": signal,
                    "confidence": int(confidence), "regime": regime, "verified": verified,
                    "has_high_impact_news": has_news,
                    "timestamp": datetime.now().isoformat()
                }
                response.update(tf_results)

                self._log_signal(symbol, signal, confidence, regime, verified)
                conn.sendall(self.encrypt(json.dumps(response)).encode('utf-8'))
            except Exception as e:
                logging.error(f"Engine Error: {e}")

    def _log_signal(self, symbol, signal, confidence, regime, verified):
        """
        Persist a trading signal record into the configured SQLite `signals` table with the current ISO timestamp.
        
        Parameters:
            symbol (str): Trading instrument identifier.
            signal (str): Signal label or direction (e.g., "buy", "sell").
            confidence (int | float): Numeric confidence score for the signal.
            regime (str): Market regime label.
            verified (bool): Whether the signal was verified; stored as `1` if True, `0` otherwise.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO signals VALUES (?,?,?,?,?,?)",
                     (datetime.now().isoformat(), symbol, signal, confidence, regime, 1 if verified else 0))
        conn.commit()
        conn.close()

    def run(self):
        """
        Start the TCP server loop, accept incoming connections, and handle each in a daemon thread.
        
        Continuously binds to the configured host and port, listens for incoming TCP connections while `self.active` is true, and spawns a daemon thread to run `handle_client` for each accepted connection. The listening socket is automatically closed when this method exits.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(10)
            logging.info(f"Brain listening on {self.host}:{self.port}")
            while self.active:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    AutonomousBrain().run()
