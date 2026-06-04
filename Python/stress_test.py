import socket
import json
import threading
import time

def simulate_client(client_id, symbol="EURUSD"):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 5555))
            request = {
                "symbol": symbol,
                "balance": 10000 + client_id * 100
            }
            s.sendall(json.dumps(request).encode('utf-8'))
            data = s.recv(4096)
            response = json.loads(data.decode('utf-8'))
            print(f"Client {client_id} - Response: {response.get('status')} | Verified: {response.get('verified')} | Signal: {response.get('signal')}")
    except Exception as e:
        print(f"Client {client_id} - Error: {e}")

def run_stress_test(num_clients=5):
    print(f"Starting Stress Test with {num_clients} concurrent clients...")
    threads = []
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURGBP"]

    for i in range(num_clients):
        t = threading.Thread(target=simulate_client, args=(i, symbols[i % len(symbols)]))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print("Stress Test completed.")

if __name__ == "__main__":
    # Note: main_engine.py must be running for this test to succeed
    run_stress_test()
