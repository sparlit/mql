import pytest
from src.shared.utils.bus import bus

@pytest.mark.asyncio
async def test_bus_emission():
    received = []
    async def handler(data):
        received.append(data)

    bus.subscribe("test:event", handler)
    await bus.emit("test:event", {"msg": "hello"})
    assert len(received) == 1
    assert received[0]["msg"] == "hello"

def test_vault_load():
    import json
    import os
    with open("src/vault.json", "r") as f:
        vault = json.load(f)
    assert "MASTER_KEY" in vault
    assert vault["ADMIN_USERNAME"] == "admin"
