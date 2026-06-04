import socket
import json
import threading
import time
import random

def simulate_client(client_id, symbol="EURUSD"):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10.0)
            s.connect(('127.0.0.1', 5555))

            # Stress Test Scenarios:
            # 1. Normal Request
            # 2. Extreme Balance
            # 3. Rare Symbol

            scenarios = [
                {"symbol": symbol, "balance": 10000, "tick_value": 1.0, "tick_size": 0.00001},
                {"symbol": "BTCUSD", "balance": 1000000, "tick_value": 0.01, "tick_size": 0.01},
                {"symbol": symbol, "balance": 100, "tick_value": 1.0, "tick_size": 0.00001}, # Low balance
            ]

            request = random.choice(scenarios)
            s.sendall(json.dumps(request).encode('utf-8'))

            data = s.recv(8192)
            if not data:
                print(f"Client {client_id} - No data received")
                return

            response = json.loads(data.decode('utf-8'))
            print(f"Client {client_id} [{request['symbol']}] - Status: {response.get('status')} | Verified: {response.get('verified')} | Confidence: {response.get('confidence')} | Regime: {response.get('regime')}")

            # Verify all 9 TFs are present
            tfs = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN']
            missing = [tf for tf in tfs if tf not in response]
            if missing:
                print(f"Client {client_id} - MISSING TFs: {missing}")
            else:
                print(f"Client {client_id} - Full Spectrum Data Verified.")

    except socket.timeout:
        print(f"Client {client_id} - Connection Timeout")
    except Exception as e:
        print(f"Client {client_id} - Error: {e}")

def run_stress_test(num_clients=10):
    print("="*60)
    print(f"STARTING COMPREHENSIVE RECURSIVE STRESS TEST - {num_clients} CLIENTS")
    print("="*60)

    threads = []
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP", "USDCAD", "USDCHF"]

    for i in range(num_clients):
        t = threading.Thread(target=simulate_client, args=(i, random.choice(symbols)))
        threads.append(t)
        t.start()
        time.sleep(0.5) # staggered start

    for t in threads:
        t.join()

    print("="*60)
    print("COMPREHENSIVE STRESS TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    run_stress_test()
