"""
Tests for stress_test.py - StressTestClient class.

Tests cover:
- encrypt / decrypt roundtrip
- encrypt produces valid base64
- decrypt handles padding stripping
- simulate: connection refused, successful flow with mocked socket
- run_stress_test: threads are started and joined
- Key consistency between StressTestClient and AutonomousBrain
"""
import pytest
import sys
import os
import json
import base64
import socket
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.dirname(__file__))

from stress_test import StressTestClient, run_stress_test


# ---------------------------------------------------------------------------
# StressTestClient: encrypt / decrypt
# ---------------------------------------------------------------------------

class TestStressTestClientEncryptDecrypt:
    @pytest.fixture()
    def client(self):
        return StressTestClient()

    def test_encrypt_returns_string(self, client):
        result = client.encrypt("hello")
        assert isinstance(result, str)

    def test_encrypt_is_valid_base64(self, client):
        result = client.encrypt("hello world")
        # Should decode without raising
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_roundtrip_simple_string(self, client):
        plaintext = "test message"
        encrypted = client.encrypt(plaintext)
        decrypted = client.decrypt(encrypted)
        assert decrypted == plaintext

    def test_roundtrip_json_payload(self, client):
        payload = json.dumps({"symbol": "EURUSD", "balance": 10000})
        encrypted = client.encrypt(payload)
        decrypted = client.decrypt(encrypted)
        assert json.loads(decrypted) == {"symbol": "EURUSD", "balance": 10000}

    def test_roundtrip_empty_string(self, client):
        encrypted = client.encrypt("")
        decrypted = client.decrypt(encrypted)
        assert decrypted == ""

    def test_roundtrip_long_string(self, client):
        long_text = "X" * 1024
        encrypted = client.encrypt(long_text)
        decrypted = client.decrypt(encrypted)
        assert decrypted == long_text

    def test_encrypt_different_plaintexts_differ(self, client):
        enc1 = client.encrypt("buy")
        enc2 = client.encrypt("sell")
        assert enc1 != enc2

    def test_encrypt_same_plaintext_consistent(self, client):
        """With a static IV, same plaintext always yields same ciphertext."""
        enc1 = client.encrypt("consistent")
        enc2 = client.encrypt("consistent")
        assert enc1 == enc2

    def test_decrypt_strips_null_bytes(self, client):
        """Decrypted output with trailing nulls should be stripped."""
        encrypted = client.encrypt("clean")
        decrypted = client.decrypt(encrypted)
        assert "\x00" not in decrypted

    def test_key_matches_brain_key(self, client):
        """The static key used by StressTestClient must match AutonomousBrain."""
        expected_key = b"Static32ByteKeyForZeroStubPolicy"
        assert client.key == expected_key

    def test_iv_matches_brain_iv(self, client):
        expected_iv = b"Static16ByteIV!!"
        assert client.iv == expected_iv

    def test_cross_compatibility_encrypt_decrypt(self, client):
        """Encrypt with client, decrypt simulating Brain logic (same key/iv)."""
        from cryptography.hazmat.primitives import padding as crypto_padding
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        original = '{"symbol": "USDJPY", "balance": 50000}'
        encrypted_b64 = client.encrypt(original)

        # Decrypt manually using same keys
        raw = base64.b64decode(encrypted_b64)
        cipher = Cipher(algorithms.AES(client.key), modes.CBC(client.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(raw) + decryptor.finalize()
        decrypted = padded_data.decode("utf-8", errors="ignore").split("\x00")[0].rstrip(
            "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
        )
        assert decrypted == original


# ---------------------------------------------------------------------------
# StressTestClient: simulate
# ---------------------------------------------------------------------------

class TestStressTestClientSimulate:
    @pytest.fixture()
    def client(self):
        return StressTestClient()

    def _make_mock_socket(self, response_data):
        mock_sock = MagicMock()
        mock_sock.__enter__ = lambda s: mock_sock
        mock_sock.__exit__ = MagicMock(return_value=False)
        mock_sock.recv.return_value = response_data
        return mock_sock

    def test_simulate_handles_connection_refused(self, client):
        """ConnectionRefusedError should be caught and logged, not raised."""
        with patch("stress_test.socket.socket") as mock_socket_cls:
            mock_sock = MagicMock()
            mock_sock.__enter__ = lambda s: mock_sock
            mock_sock.__exit__ = MagicMock(return_value=False)
            mock_sock.connect.side_effect = ConnectionRefusedError("Connection refused")
            mock_socket_cls.return_value = mock_sock
            # Should not raise
            client.simulate(0, "EURUSD")

    def test_simulate_handles_timeout(self, client):
        """Timeout should be caught and not propagate."""
        with patch("stress_test.socket.socket") as mock_socket_cls:
            mock_sock = MagicMock()
            mock_sock.__enter__ = lambda s: mock_sock
            mock_sock.__exit__ = MagicMock(return_value=False)
            mock_sock.connect.side_effect = socket.timeout("timed out")
            mock_socket_cls.return_value = mock_sock
            client.simulate(1, "GBPUSD")

    def test_simulate_sends_encrypted_payload(self, client):
        """simulate() should call sendall with an encrypted payload."""
        response_json = json.dumps({"status": "success", "signal": "BUY"})
        encrypted_response = client.encrypt(response_json).encode("utf-8")

        with patch("stress_test.socket.socket") as mock_socket_cls:
            mock_sock = MagicMock()
            mock_sock.__enter__ = lambda s: mock_sock
            mock_sock.__exit__ = MagicMock(return_value=False)
            mock_sock.recv.return_value = encrypted_response
            mock_socket_cls.return_value = mock_sock

            client.simulate(0, "EURUSD")

        mock_sock.sendall.assert_called_once()
        sent_bytes = mock_sock.sendall.call_args[0][0]
        assert isinstance(sent_bytes, bytes)
        # Should be valid base64
        base64.b64decode(sent_bytes)

    def test_simulate_with_empty_response_no_crash(self, client):
        """Empty response from server should be handled gracefully."""
        with patch("stress_test.socket.socket") as mock_socket_cls:
            mock_sock = MagicMock()
            mock_sock.__enter__ = lambda s: mock_sock
            mock_sock.__exit__ = MagicMock(return_value=False)
            mock_sock.recv.return_value = b""
            mock_socket_cls.return_value = mock_sock

            client.simulate(0, "EURUSD")

    def test_simulate_sets_timeout_on_socket(self, client):
        response_json = json.dumps({"status": "success", "signal": "NEUTRAL"})
        encrypted_response = client.encrypt(response_json).encode("utf-8")

        with patch("stress_test.socket.socket") as mock_socket_cls:
            mock_sock = MagicMock()
            mock_sock.__enter__ = lambda s: mock_sock
            mock_sock.__exit__ = MagicMock(return_value=False)
            mock_sock.recv.return_value = encrypted_response
            mock_socket_cls.return_value = mock_sock

            client.simulate(0, "EURUSD")

        mock_sock.settimeout.assert_called_once_with(10.0)

    def test_simulate_connects_to_correct_address(self, client):
        response_json = json.dumps({"status": "success", "signal": "BUY"})
        encrypted_response = client.encrypt(response_json).encode("utf-8")

        with patch("stress_test.socket.socket") as mock_socket_cls:
            mock_sock = MagicMock()
            mock_sock.__enter__ = lambda s: mock_sock
            mock_sock.__exit__ = MagicMock(return_value=False)
            mock_sock.recv.return_value = encrypted_response
            mock_socket_cls.return_value = mock_sock

            client.simulate(0, "EURUSD")

        mock_sock.connect.assert_called_once_with(("127.0.0.1", 5555))


# ---------------------------------------------------------------------------
# run_stress_test
# ---------------------------------------------------------------------------

class TestRunStressTest:
    def test_launches_correct_number_of_threads(self):
        with patch("stress_test.StressTestClient") as mock_client_cls, \
             patch("stress_test.time.sleep"):
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            run_stress_test(num_clients=5)
        assert mock_client.simulate.call_count == 5

    def test_uses_eurusd_symbol(self):
        with patch("stress_test.StressTestClient") as mock_client_cls, \
             patch("stress_test.time.sleep"):
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            run_stress_test(num_clients=3)

        for call_args in mock_client.simulate.call_args_list:
            assert call_args[0][1] == "EURUSD"

    def test_default_num_clients_is_3(self):
        with patch("stress_test.StressTestClient") as mock_client_cls, \
             patch("stress_test.time.sleep"):
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            run_stress_test()
        assert mock_client.simulate.call_count == 3

    def test_client_ids_are_sequential(self):
        with patch("stress_test.StressTestClient") as mock_client_cls, \
             patch("stress_test.time.sleep"):
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            run_stress_test(num_clients=4)

        client_ids = [call_args[0][0] for call_args in mock_client.simulate.call_args_list]
        assert sorted(client_ids) == list(range(4))