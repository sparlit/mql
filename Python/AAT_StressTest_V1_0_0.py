import socket
import json
import threading
import time
import random
import logging

# Configure logging for stress test
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def simulate_client(client_id, symbol="EURUSD"):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect(('127.0.0.1', 5555))

            scenarios = [
                # 1. Normal Request
                {"symbol": symbol, "balance": 10000, "tick_value": 1.0, "tick_size": 0.00001, "sl_points": 200},
                # 2. Extreme Balance
                {"symbol": "BTCUSD", "balance": 1000000, "tick_value": 0.01, "tick_size": 0.01, "sl_points": 500},
                # 3. Low balance / Small SL
                {"symbol": "XAUUSD.pro", "balance": 100, "tick_value": 1.0, "tick_size": 0.01, "sl_points": 10},
                # 4. Non-standard symbol
                {"symbol": "US30", "balance": 50000, "tick_value": 1.0, "tick_size": 0.1, "sl_points": 100},
                # 5. Malformed JSON (Handled below by sending raw)
            ]

            request = random.choice(scenarios)

            # 10% chance to send malformed data
            if random.random() < 0.1:
                logging.info(f"Client {client_id} sending malformed JSON...")
                s.sendall(b'{"symbol": "EURUSD", "balance": 10000, "invalid_json": ')
            else:
                s.sendall(json.dumps(request).encode('utf-8'))

            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk: break
                data += chunk
                if data.endswith(b'}'): break

            if not data:
                logging.warning(f"Client {client_id} - No data received")
                return

            try:
                response = json.loads(data.decode('utf-8'))
                logging.info(f"Client {client_id} [{request.get('symbol')}] - Status: {response.get('status')} | Verified: {response.get('verified')} | Lot: {response.get('recommended_lot')}")
            except Exception as e:
                logging.error(f"Client {client_id} - JSON Error: {e} | Raw Data: {data}")

    except socket.timeout:
        logging.error(f"Client {client_id} - Connection Timeout")
    except ConnectionRefusedError:
        logging.error(f"Client {client_id} - Connection Refused (Is main_engine.py running?)")
    except Exception as e:
        logging.error(f"Client {client_id} - Error: {e}")

def run_stress_test(num_clients=50):
    logging.info("="*60)
    logging.info(f"STARTING COMPREHENSIVE FULL-SPECTRUM STRESS TEST - {num_clients} CLIENTS")
    logging.info("="*60)

    threads = []
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", "USDCAD", "USDCHF", "XAUUSD", "BTCUSD"]

    for i in range(num_clients):
        t = threading.Thread(target=simulate_client, args=(i, random.choice(symbols)))
        threads.append(t)
        t.start()
        time.sleep(random.uniform(0.1, 0.3)) # staggered start

    for t in threads:
        t.join()

    logging.info("="*60)
    logging.info("COMPREHENSIVE STRESS TEST COMPLETED")
    logging.info("="*60)

if __name__ == "__main__":
    run_stress_test()
