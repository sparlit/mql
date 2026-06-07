# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: MQL5/Socket Ingress Plugin with AES-256 Decryption

import socket
import asyncio
import json
import logging
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from src.shared.utils.bus import bus

# Load Vault for Key
VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "vault.json")
with open(VAULT_PATH, "r") as f:
    vault = json.load(f)
MASTER_KEY = vault.get("MASTER_KEY", "AAT_SECURE_FOSS_KEY_256_BIT_STRIP").encode()[:32].ljust(32, b'\0')

class Decryptor:
    @staticmethod
    def decrypt(ct_b64):
        try:
            combined = base64.b64decode(ct_b64)
            iv, ct = combined[:16], combined[16:]
            cipher = Cipher(algorithms.AES(MASTER_KEY), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ct) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            return (unpadder.update(padded_data) + unpadder.finalize()).decode()
        except Exception as e:
            logging.error(f"Decryption failed: {e}")
            return None

class SocketIngressPlugin:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        logging.info(f"Sovereign Ingress active on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        try:
            data = await reader.read(10240)
            if not data: return

            raw_message = data.decode().strip()
            decrypted = Decryptor.decrypt(raw_message)

            if decrypted:
                payload = json.loads(decrypted)
                logging.debug(f"Decrypted payload: {payload.get('symbol')}")

                # Emit to bus for intelligence/risk processing
                await bus.emit("data:market_update", payload)

                # Simple Success Response
                resp = {"status": "success", "health": "OK", "timestamp": os.getpid()}
                # Note: In production, the response should also be encrypted.
                # For this step, we focus on ingress decryption.
                writer.write(json.dumps(resp).encode() + b"\n")
                await writer.drain()

            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logging.error(f"Ingress handler error: {e}")

async def run_ingress():
    ingress = SocketIngressPlugin()
    await ingress.start()
