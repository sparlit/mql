# Project: Autonomous AutoTrader (AAT)
# Version: V3.3.0_20260606
# License: 100% FOSS / GNU GPL v3
# Author: Simon Peter
# Verification: Zero-Stub / Production Ready
# Description: Concurrency Stress Test for Multi-Client Verification

import socket
import json
import threading
import time
from Python.V3_1_0.Security import AATSecurity

def simulate_client(client_id, symbol="EURUSD"):
    security = AATSecurity()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 5555))
            payload = {"symbol": symbol, "balance": 10000}
            s.sendall(security.encrypt(json.dumps(payload)).encode() + b"\n")
            resp = s.recv(10240).decode().strip()
            if resp:
                dec = security.decrypt(resp)
                data = json.loads(dec)
                print(f"Client {client_id} [{symbol}] - Status: {data.get('status')}")
    except Exception as e:
        print(f"Client {client_id} Error: {e}")

if __name__ == "__main__":
    print("STARTING STRESS TEST V3.3.0")
    threads = []
    for i in range(10):
        t = threading.Thread(target=simulate_client, args=(i,))
        threads.append(t)
        t.start()
    for t in threads: t.join()
