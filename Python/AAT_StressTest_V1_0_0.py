import socket
import json
import threading
import time
import random
import logging
from AAT_Security_V1_0_0 import AATSecurity

# Configure logging for stress test
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class StressTestClient:
    def __init__(self):
        self.security = AATSecurity()

    def simulate(self, client_id, symbol="EURUSD"):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10.0)
                s.connect(('127.0.0.1', 5555))

                request = {
                    "symbol": symbol,
                    "balance": 10000,
                    "tick_value": 1.0,
                    "sl_points": 200,
                    "current_profit_pips": 0
                }

                # 10% chance to send malformed data
                if random.random() < 0.1:
                    logging.info(f"Client {client_id} sending malformed data...")
                    s.sendall(b'ThisIsNotEncrypted!!!\n')
                else:
                    payload = self.security.encrypt(json.dumps(request)) + "\n"
                    s.sendall(payload.encode('utf-8'))

                    data_raw_bytes = b""
                    while True:
                        chunk = s.recv(4096)
                        if not chunk: break
                        data_raw_bytes += chunk
                        if b'\n' in chunk: break

                    if not data_raw_bytes:
                        logging.warning(f"Client {client_id} received no response")
                        return

                    resp_str = data_raw_bytes.decode('utf-8').strip()
                    decrypted_resp = self.security.decrypt(resp_str)

                    if not decrypted_resp:
                        logging.error(f"Client {client_id} failed to decrypt response")
                        return

                    response = json.loads(decrypted_resp)
                    logging.info(f"Client {client_id} [{symbol}] - Status: {response.get('status')} | Signal: {response.get('signal')}")
        except Exception as e:
            logging.error(f"Client {client_id} Error: {e}")

def run_stress_test(num_clients=5):
    logging.info("="*60)
    logging.info(f"STARTING COMPREHENSIVE STRESS TEST - {num_clients} CLIENTS")
    logging.info("="*60)
    client = StressTestClient()
    threads = []
    for i in range(num_clients):
        t = threading.Thread(target=client.simulate, args=(i, "EURUSD"))
        threads.append(t)
        t.start()
        time.sleep(0.5)
    for t in threads: t.join()

if __name__ == "__main__":
    run_stress_test()
