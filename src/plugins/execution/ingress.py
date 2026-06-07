# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: MQL5/Socket Ingress Plugin

import socket
import asyncio
import json
import logging
from src.core.events import bus

class SocketIngressPlugin:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logging.info(f"Socket Ingress Plugin serving on {addr}")
        print(f"Brain listening on {addr}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        data = await reader.read(10240)
        message = data.decode().strip()
        await bus.emit("ingress:raw_data", {"raw": message, "writer": writer, "type": "mql5"})

async def run_ingress():
    ingress = SocketIngressPlugin()
    await ingress.start()
