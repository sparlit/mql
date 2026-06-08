import pytest
import os
import json
from src.shared.utils.bus import bus
from src.core.auth import create_access_token, verify_token

def test_vault_load():
    with open("src/vault.json", "r") as f:
        vault = json.load(f)
    assert "MASTER_KEY" in vault
    assert "ADMIN_USERNAME" in vault

@pytest.mark.asyncio
async def test_event_bus():
    received = []
    async def callback(data):
        received.append(data)

    bus.subscribe("test_event", callback)
    await bus.emit("test_event", {"msg": "hello"})
    assert len(received) == 1
    assert received[0]["msg"] == "hello"

def test_auth_token():
    token = create_access_token(data={"sub": "admin", "type": "access"})
    payload = verify_token(token, "access")
    assert payload["sub"] == "admin"
    assert payload["type"] == "access"

def test_auth_token_invalid():
    token = create_access_token(data={"sub": "admin", "type": "access"})
    payload = verify_token(token, "refresh")
    assert payload is None
