# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: MQL5/Socket Ingress Plugin for Microkernel

import socket
import asyncio
import json
import logging
from src.core.main import bus

class SocketIngressPlugin:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.active = True

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logging.info(f"Socket Ingress Plugin serving on {addr}")
        print(f"Brain listening on {addr}") # Compatibility for CI
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        data = await reader.read(10240)
        message = data.decode().strip()
        addr = writer.get_extra_info('peername')

        logging.debug(f"Received data from {addr}")
        await bus.emit("ingress:raw_data", {"raw": message, "writer": writer, "type": "mql5"})

async def run_ingress():
    ingress = SocketIngressPlugin()
    await ingress.start()
