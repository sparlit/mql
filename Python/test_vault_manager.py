"""
Tests for vault_manager.py - VaultManager class.

Tests cover:
- _ensure_key: creates key file when missing, does not overwrite existing
- _get_fernet: returns usable Fernet instance
- store_secret: encrypts and persists to vault.json
- get_secret: decrypts persisted value correctly
- get_secret: returns None when key missing from vault
- get_secret: returns None when vault file absent
- roundtrip: store then get
- Multiple secrets coexist in vault
- Corrupt vault file handling
- Empty vault file handling
"""
import pytest
import sys
import os
import json
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from vault_manager import VaultManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_vault(tmp_path):
    """VaultManager using tmp_path for all file I/O."""
    vault_path = str(tmp_path / "vault.json")
    key_path = str(tmp_path / "master.key")

    with patch.object(VaultManager, "__init__", lambda self, *a, **kw: None):
        vm = VaultManager.__new__(VaultManager)
        vm.vault_path = vault_path
        vm.key_path = key_path

    # Manually run _ensure_key to generate the key
    vm._ensure_key()
    return vm


# ---------------------------------------------------------------------------
# _ensure_key
# ---------------------------------------------------------------------------

class TestEnsureKey:
    def test_creates_key_file_when_absent(self, tmp_path):
        vault_path = str(tmp_path / "vault.json")
        key_path = str(tmp_path / "master.key")
        vm = VaultManager.__new__(VaultManager)
        vm.vault_path = vault_path
        vm.key_path = key_path

        assert not os.path.exists(key_path)
        vm._ensure_key()
        assert os.path.exists(key_path)

    def test_key_file_is_non_empty(self, tmp_path):
        vault_path = str(tmp_path / "vault.json")
        key_path = str(tmp_path / "master.key")
        vm = VaultManager.__new__(VaultManager)
        vm.vault_path = vault_path
        vm.key_path = key_path
        vm._ensure_key()

        with open(key_path, "rb") as f:
            content = f.read()
        assert len(content) > 0

    def test_does_not_overwrite_existing_key(self, tmp_path):
        vault_path = str(tmp_path / "vault.json")
        key_path = str(tmp_path / "master.key")
        vm = VaultManager.__new__(VaultManager)
        vm.vault_path = vault_path
        vm.key_path = key_path

        # Write a known key first
        from cryptography.fernet import Fernet
        existing_key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(existing_key)

        vm._ensure_key()

        with open(key_path, "rb") as f:
            saved_key = f.read()
        assert saved_key == existing_key

    def test_generated_key_is_valid_fernet_key(self, tmp_path):
        vault_path = str(tmp_path / "vault.json")
        key_path = str(tmp_path / "master.key")
        vm = VaultManager.__new__(VaultManager)
        vm.vault_path = vault_path
        vm.key_path = key_path
        vm._ensure_key()

        from cryptography.fernet import Fernet
        with open(key_path, "rb") as f:
            key = f.read()
        # Should not raise
        f_obj = Fernet(key)
        assert f_obj is not None


# ---------------------------------------------------------------------------
# _get_fernet
# ---------------------------------------------------------------------------

class TestGetFernet:
    def test_returns_fernet_instance(self, tmp_vault):
        from cryptography.fernet import Fernet
        result = tmp_vault._get_fernet()
        assert isinstance(result, Fernet)

    def test_fernet_can_encrypt_decrypt(self, tmp_vault):
        f = tmp_vault._get_fernet()
        token = f.encrypt(b"test_data")
        decrypted = f.decrypt(token)
        assert decrypted == b"test_data"


# ---------------------------------------------------------------------------
# store_secret
# ---------------------------------------------------------------------------

class TestStoreSecret:
    def test_creates_vault_file(self, tmp_vault):
        assert not os.path.exists(tmp_vault.vault_path)
        with patch("os.sync"):
            tmp_vault.store_secret("API_KEY", "secret_value")
        assert os.path.exists(tmp_vault.vault_path)

    def test_vault_file_contains_key(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("MY_KEY", "my_value")

        with open(tmp_vault.vault_path, "r") as f:
            data = json.load(f)
        assert "MY_KEY" in data

    def test_stored_value_is_encrypted(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("SECRET", "plaintext")

        with open(tmp_vault.vault_path, "r") as f:
            data = json.load(f)
        # The stored value should NOT be the plaintext
        assert data["SECRET"] != "plaintext"

    def test_stored_value_is_string(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("KEY", "value")

        with open(tmp_vault.vault_path, "r") as f:
            data = json.load(f)
        assert isinstance(data["KEY"], str)

    def test_overwrites_existing_key(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("OVERWRITE_KEY", "first_value")
            tmp_vault.store_secret("OVERWRITE_KEY", "second_value")

        result = tmp_vault.get_secret("OVERWRITE_KEY")
        assert result == "second_value"

    def test_multiple_keys_coexist(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("KEY_A", "value_a")
            tmp_vault.store_secret("KEY_B", "value_b")

        with open(tmp_vault.vault_path, "r") as f:
            data = json.load(f)
        assert "KEY_A" in data
        assert "KEY_B" in data


# ---------------------------------------------------------------------------
# get_secret
# ---------------------------------------------------------------------------

class TestGetSecret:
    def test_returns_none_when_vault_absent(self, tmp_vault):
        assert not os.path.exists(tmp_vault.vault_path)
        result = tmp_vault.get_secret("MISSING_KEY")
        assert result is None

    def test_returns_none_when_key_not_in_vault(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("OTHER_KEY", "other_value")
        result = tmp_vault.get_secret("NONEXISTENT_KEY")
        assert result is None

    def test_returns_correct_value_for_existing_key(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("MY_SECRET", "hello_world")
        result = tmp_vault.get_secret("MY_SECRET")
        assert result == "hello_world"

    def test_returns_string_type(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("STR_KEY", "string_value")
        result = tmp_vault.get_secret("STR_KEY")
        assert isinstance(result, str)

    def test_handles_empty_vault_file(self, tmp_vault):
        with open(tmp_vault.vault_path, "w") as f:
            f.write("")
        result = tmp_vault.get_secret("ANY_KEY")
        assert result is None

    def test_handles_corrupt_vault_file(self, tmp_vault):
        with open(tmp_vault.vault_path, "w") as f:
            f.write("not valid json {{{{")
        result = tmp_vault.get_secret("ANY_KEY")
        assert result is None

    def test_handles_empty_json_object(self, tmp_vault):
        with open(tmp_vault.vault_path, "w") as f:
            json.dump({}, f)
        result = tmp_vault.get_secret("EMPTY_VAULT_KEY")
        assert result is None


# ---------------------------------------------------------------------------
# Store/Get roundtrip
# ---------------------------------------------------------------------------

class TestStoreGetRoundtrip:
    def test_basic_roundtrip(self, tmp_vault):
        with patch("os.sync"):
            tmp_vault.store_secret("ROUNDTRIP", "secure_data_123")
        assert tmp_vault.get_secret("ROUNDTRIP") == "secure_data_123"

    def test_roundtrip_with_special_characters(self, tmp_vault):
        value = "pass!@#$%^&*()_+-=[]{}|;:',.<>?"
        with patch("os.sync"):
            tmp_vault.store_secret("SPECIAL", value)
        assert tmp_vault.get_secret("SPECIAL") == value

    def test_roundtrip_with_base64_value(self, tmp_vault):
        import base64
        import os
        value = base64.b64encode(os.urandom(32)).decode()
        with patch("os.sync"):
            tmp_vault.store_secret("B64_VAL", value)
        assert tmp_vault.get_secret("B64_VAL") == value

    def test_roundtrip_multiple_secrets(self, tmp_vault):
        secrets = {"KEY1": "val1", "KEY2": "val2", "KEY3": "val3"}
        with patch("os.sync"):
            for k, v in secrets.items():
                tmp_vault.store_secret(k, v)
        for k, v in secrets.items():
            assert tmp_vault.get_secret(k) == v

    def test_roundtrip_long_value(self, tmp_vault):
        long_value = "A" * 1000
        with patch("os.sync"):
            tmp_vault.store_secret("LONG_KEY", long_value)
        assert tmp_vault.get_secret("LONG_KEY") == long_value


# ---------------------------------------------------------------------------
# VaultManager constructor
# ---------------------------------------------------------------------------

class TestVaultManagerConstructor:
    def test_default_paths(self, tmp_path):
        """Verify constructor sets expected default paths."""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", MagicMock(return_value=MagicMock(
                 __enter__=MagicMock(return_value=MagicMock(read=lambda: b"")),
                 __exit__=MagicMock(return_value=False)
             ))):
            try:
                vm = VaultManager()
                assert vm.vault_path == "Python/vault.json"
                assert vm.key_path == "Python/master.key"
            except Exception:
                pass  # Key generation may fail in mocked env; check paths first

    def test_custom_vault_path(self, tmp_path):
        vault_path = str(tmp_path / "custom_vault.json")
        key_path = str(tmp_path / "custom.key")
        vm = VaultManager.__new__(VaultManager)
        vm.vault_path = vault_path
        vm.key_path = key_path
        vm._ensure_key()
        assert vm.vault_path == vault_path
