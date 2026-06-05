import socket
import json
import threading
import time
import random
import logging
import base64
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from vault_manager import VaultManager

# Configure logging for stress test
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class StressTestClient:
    def __init__(self):
        self.vault = VaultManager()
        self.key = base64.b64decode(self.vault.get_secret("COMM_KEY"))

    def encrypt(self, plaintext):
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + encrypted).decode('utf-8')

    def decrypt(self, encrypted_b64):
        raw = base64.b64decode(encrypted_b64)
        iv = raw[:16]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(raw[16:]) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return (unpadder.update(padded_data) + unpadder.finalize()).decode('utf-8')

    def simulate(self, client_id, symbol="EURUSD"):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10.0)
                s.connect(('127.0.0.1', 5555))

                request = {"symbol": symbol, "balance": 10000}
                s.sendall(self.encrypt(json.dumps(request)).encode('utf-8'))

                data_raw = s.recv(16384).decode('utf-8')
                if not data_raw: return

                response = json.loads(self.decrypt(data_raw))
                logging.info(f"Client {client_id} [{symbol}] - Status: {response.get('status')} | Signal: {response.get('signal')}")
        except Exception as e:
            logging.error(f"Client {client_id} Error: {e}")

import os

def run_stress_test(num_clients=3):
    client = StressTestClient()
    threads = []
    for i in range(num_clients):
        t = threading.Thread(target=client.simulate, args=(i, "EURUSD"))
        threads.append(t)
        t.start()
        time.sleep(1)
    for t in threads: t.join()

if __name__ == "__main__":
    run_stress_test()
