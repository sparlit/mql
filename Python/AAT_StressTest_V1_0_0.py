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
import os

# Configure logging for stress test
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class StressTestClient:
    def __init__(self):
        # Static keys matching Brain and MQL5
        self.key = b"Static32ByteKeyForZeroStubPolicy"
        self.iv = b"Static16ByteIV!!"

    def encrypt(self, plaintext):
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_b64):
        raw = base64.b64decode(encrypted_b64)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(raw) + decryptor.finalize()
        return padded_data.decode('utf-8', errors='ignore').split('\x00')[0].rstrip('\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10')

    def simulate(self, client_id, symbol="EURUSD"):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10.0)
                s.connect(('127.0.0.1', 5555))

                request = {"symbol": symbol, "balance": 10000}
                payload = self.encrypt(json.dumps(request))
                s.sendall(payload.encode('utf-8'))

                data_raw = s.recv(16384).decode('utf-8')
                if not data_raw: return

                response = json.loads(self.decrypt(data_raw))
                logging.info(f"Client {client_id} [{symbol}] - Status: {response.get('status')} | Signal: {response.get('signal')}")
        except Exception as e:
            logging.error(f"Client {client_id} Error: {e}")

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
