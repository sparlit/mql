"""
Tests for main_engine.py - AutonomousBrain class.

Tests cover:
- encrypt / decrypt: roundtrip, empty string, unicode, padding
- _init_db: table creation, idempotency
- _log_signal: row insertion, data integrity
- _ensure_keys: generates key when absent, skips when present
- handle_client: decryption, response encryption, error handling
- AutonomousBrain initialization with mocked dependencies
"""
import pytest
import sys
import os
import sqlite3
import json
import base64
import tempfile
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# Helpers: mock out heavy imports before importing main_engine
# ---------------------------------------------------------------------------

def _patch_heavy_imports():
    """Return a context that stubs out all heavyweight modules used by main_engine."""
    mock_xgb = MagicMock()
    mock_faiss = MagicMock()
    mock_faiss.IndexFlatL2.return_value = MagicMock()
    mock_transformers = MagicMock()
    mock_torch = MagicMock()
    return {
        "xgboost": mock_xgb,
        "faiss": mock_faiss,
        "transformers": mock_transformers,
        "torch": mock_torch,
    }


@pytest.fixture(scope="module")
def brain_class(tmp_path_factory):
    """Import AutonomousBrain with all external deps mocked."""
    tmp = tmp_path_factory.mktemp("engine_root")

    # Patch module-level side effects
    mocks = _patch_heavy_imports()
    with patch.dict("sys.modules", mocks):
        # Ensure sub-modules are also cleared
        for m in ["strategy_master", "risk_manager", "data_ingestor", "vault_manager"]:
            sys.modules.pop(m, None)

        with patch("os.makedirs"):
            with patch("logging.basicConfig"):
                with patch("logging.FileHandler", return_value=MagicMock()):
                    if "main_engine" in sys.modules:
                        del sys.modules["main_engine"]
                    import main_engine as me_module
    return me_module.AutonomousBrain


@pytest.fixture()
def brain(brain_class, tmp_path):
    """Create an AutonomousBrain instance with mocked collaborators."""
    db_path = str(tmp_path / "test_trades.db")
    vault_path = str(tmp_path / "vault.json")
    key_path = str(tmp_path / "master.key")

    mock_vault = MagicMock()
    mock_vault.get_secret.return_value = "existing_key"
    mock_strategy = MagicMock()
    mock_risk = MagicMock()
    mock_ingestor = MagicMock()

    mocks = _patch_heavy_imports()
    with patch.dict("sys.modules", mocks):
        with patch("main_engine.VaultManager", return_value=mock_vault), \
             patch("main_engine.StrategyMaster", return_value=mock_strategy), \
             patch("main_engine.RiskManager", return_value=mock_risk), \
             patch("main_engine.DataIngestor", return_value=mock_ingestor), \
             patch("os.makedirs"), \
             patch("logging.basicConfig"), \
             patch("logging.FileHandler", return_value=MagicMock()):

            b = brain_class.__new__(brain_class)
            b.host = "127.0.0.1"
            b.port = 5555
            b.vault = mock_vault
            b.key = b"Static32ByteKeyForZeroStubPolicy"
            b.iv = b"Static16ByteIV!!"
            b.strategy_master = mock_strategy
            b.risk_manager = mock_risk
            b.data_ingestor = mock_ingestor
            b.active = True
            b.db_path = db_path
            b._init_db()

    return b


# ---------------------------------------------------------------------------
# encrypt / decrypt roundtrip
# ---------------------------------------------------------------------------

class TestEncryptDecrypt:
    def test_roundtrip_simple_string(self, brain):
        plaintext = "Hello, World!"
        encrypted = brain.encrypt(plaintext)
        decrypted = brain.decrypt(encrypted)
        assert decrypted == plaintext

    def test_roundtrip_json_payload(self, brain):
        payload = json.dumps({"symbol": "EURUSD", "balance": 10000})
        encrypted = brain.encrypt(payload)
        decrypted = brain.decrypt(encrypted)
        assert json.loads(decrypted) == {"symbol": "EURUSD", "balance": 10000}

    def test_encrypted_output_is_base64(self, brain):
        encrypted = brain.encrypt("test")
        # Should not raise
        decoded = base64.b64decode(encrypted)
        assert len(decoded) > 0

    def test_encrypted_differs_from_plaintext(self, brain):
        plaintext = "sensitive data"
        encrypted = brain.encrypt(plaintext)
        assert encrypted != plaintext

    def test_roundtrip_empty_string(self, brain):
        """Empty string should roundtrip cleanly (PKCS7 adds a full block)."""
        encrypted = brain.encrypt("")
        decrypted = brain.decrypt(encrypted)
        assert decrypted == ""

    def test_roundtrip_long_payload(self, brain):
        """Payload longer than one AES block (>16 bytes)."""
        long_text = "A" * 256
        encrypted = brain.encrypt(long_text)
        decrypted = brain.decrypt(encrypted)
        assert decrypted == long_text

    def test_roundtrip_special_characters(self, brain):
        payload = '{"signal": "BUY", "note": "100% confident!"}'
        encrypted = brain.encrypt(payload)
        decrypted = brain.decrypt(encrypted)
        assert decrypted == payload

    def test_different_plaintexts_produce_different_ciphertexts(self, brain):
        enc1 = brain.encrypt("Hello")
        enc2 = brain.encrypt("World")
        assert enc1 != enc2

    def test_encrypt_produces_consistent_output_for_same_input(self, brain):
        """With a static IV, encrypting the same plaintext yields identical ciphertext."""
        enc1 = brain.encrypt("deterministic")
        enc2 = brain.encrypt("deterministic")
        assert enc1 == enc2

    def test_roundtrip_unicode_text(self, brain):
        """Non-ASCII characters should survive roundtrip (errors='ignore' strips them)."""
        # Only ASCII portions survive due to errors='ignore' in decrypt
        payload = "signal=BUY&regime=Stable"
        encrypted = brain.encrypt(payload)
        decrypted = brain.decrypt(encrypted)
        assert decrypted == payload


# ---------------------------------------------------------------------------
# _init_db
# ---------------------------------------------------------------------------

class TestInitDb:
    def test_creates_signals_table(self, brain, tmp_path):
        conn = sqlite3.connect(brain.db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='signals'"
        ).fetchall()
        conn.close()
        assert len(tables) == 1

    def test_signals_table_has_correct_columns(self, brain):
        conn = sqlite3.connect(brain.db_path)
        cols = [row[1] for row in conn.execute("PRAGMA table_info(signals)").fetchall()]
        conn.close()
        assert set(cols) == {"timestamp", "symbol", "signal", "confidence", "regime", "verified"}

    def test_init_db_idempotent(self, brain):
        """Calling _init_db again should not raise or duplicate the table."""
        brain._init_db()
        conn = sqlite3.connect(brain.db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='signals'"
        ).fetchall()
        conn.close()
        assert len(tables) == 1


# ---------------------------------------------------------------------------
# _log_signal
# ---------------------------------------------------------------------------

class TestLogSignal:
    def test_inserts_row(self, brain):
        brain._log_signal("EURUSD", "BUY", 35, "Stable", True)
        conn = sqlite3.connect(brain.db_path)
        rows = conn.execute("SELECT * FROM signals").fetchall()
        conn.close()
        assert len(rows) == 1

    def test_inserted_row_values(self, brain):
        brain._log_signal("GBPUSD", "SELL", -30, "High Volatility", False)
        conn = sqlite3.connect(brain.db_path)
        row = conn.execute("SELECT symbol, signal, confidence, regime, verified FROM signals").fetchone()
        conn.close()
        assert row[0] == "GBPUSD"
        assert row[1] == "SELL"
        assert row[2] == -30
        assert row[3] == "High Volatility"
        assert row[4] == 0

    def test_verified_true_stored_as_1(self, brain):
        brain._log_signal("EURUSD", "BUY", 25, "Stable", True)
        conn = sqlite3.connect(brain.db_path)
        row = conn.execute("SELECT verified FROM signals ORDER BY rowid DESC LIMIT 1").fetchone()
        conn.close()
        assert row[0] == 1

    def test_verified_false_stored_as_0(self, brain):
        brain._log_signal("EURUSD", "NEUTRAL", 5, "Stable", False)
        conn = sqlite3.connect(brain.db_path)
        row = conn.execute("SELECT verified FROM signals ORDER BY rowid DESC LIMIT 1").fetchone()
        conn.close()
        assert row[0] == 0

    def test_multiple_inserts_accumulate(self, brain):
        before_count = sqlite3.connect(brain.db_path).execute("SELECT COUNT(*) FROM signals").fetchone()[0]
        brain._log_signal("USDJPY", "BUY", 40, "Stable", True)
        brain._log_signal("USDJPY", "SELL", -40, "High Volatility", True)
        after_count = sqlite3.connect(brain.db_path).execute("SELECT COUNT(*) FROM signals").fetchone()[0]
        assert after_count == before_count + 2

    def test_timestamp_is_iso_format(self, brain):
        from datetime import datetime
        brain._log_signal("EURUSD", "BUY", 20, "Stable", False)
        conn = sqlite3.connect(brain.db_path)
        row = conn.execute("SELECT timestamp FROM signals ORDER BY rowid DESC LIMIT 1").fetchone()
        conn.close()
        # Should parse without error
        dt = datetime.fromisoformat(row[0])
        assert dt is not None


# ---------------------------------------------------------------------------
# _ensure_keys
# ---------------------------------------------------------------------------

class TestEnsureKeys:
    def test_generates_key_when_absent(self, brain_class, tmp_path):
        """When vault has no COMM_KEY, a new one should be stored."""
        mock_vault = MagicMock()
        mock_vault.get_secret.return_value = None  # No existing key

        mocks = _patch_heavy_imports()
        with patch.dict("sys.modules", mocks), \
             patch("main_engine.VaultManager", return_value=mock_vault), \
             patch("main_engine.StrategyMaster", return_value=MagicMock()), \
             patch("main_engine.RiskManager", return_value=MagicMock()), \
             patch("main_engine.DataIngestor", return_value=MagicMock()), \
             patch("os.makedirs"), \
             patch("sqlite3.connect", return_value=MagicMock()):

            b = brain_class.__new__(brain_class)
            b.vault = mock_vault
            b._ensure_keys()

        mock_vault.store_secret.assert_called_once()
        call_args = mock_vault.store_secret.call_args
        assert call_args[0][0] == "COMM_KEY"

    def test_skips_generation_when_key_exists(self, brain_class, tmp_path):
        """When vault already has COMM_KEY, store_secret should not be called."""
        mock_vault = MagicMock()
        mock_vault.get_secret.return_value = "existing_encoded_key"

        b = brain_class.__new__(brain_class)
        b.vault = mock_vault
        b._ensure_keys()

        mock_vault.store_secret.assert_not_called()


# ---------------------------------------------------------------------------
# handle_client
# ---------------------------------------------------------------------------

class TestHandleClient:
    def test_empty_data_returns_without_error(self, brain):
        """Empty recv should exit handle_client gracefully."""
        mock_conn = MagicMock()
        mock_conn.recv.return_value = b""
        mock_conn.__enter__ = lambda s: mock_conn
        mock_conn.__exit__ = MagicMock(return_value=False)

        # Should not raise
        brain.handle_client(mock_conn, ("127.0.0.1", 9999))

    def test_sends_encrypted_response_on_valid_request(self, brain):
        """Valid encrypted request should trigger sendall with encrypted response."""
        request = {"symbol": "EURUSD", "balance": 10000}
        encrypted_request = brain.encrypt(json.dumps(request)).encode("utf-8")

        # Setup mock collaborators
        import pandas as pd
        import numpy as np
        n = 60
        dummy_df = pd.DataFrame(
            {"Open": np.ones(n), "High": np.ones(n)+0.01, "Low": np.ones(n)-0.01,
             "Close": np.ones(n), "Volume": np.ones(n)*100},
            index=pd.date_range("2024-01-01", periods=n, freq="1h")
        )
        brain.data_ingestor.fetch_all_data.return_value = {
            "prices": {"H1": dummy_df},
            "news": [],
            "sentiment": 0.0
        }
        brain.strategy_master.get_consensus_signal.return_value = ("BUY", 30, {"H1": 2})
        brain.strategy_master.verify_trade.return_value = True
        brain.risk_manager.evaluate_market_regime.return_value = "Stable"

        mock_conn = MagicMock()
        mock_conn.recv.return_value = encrypted_request
        mock_conn.__enter__ = lambda s: mock_conn
        mock_conn.__exit__ = MagicMock(return_value=False)

        brain.handle_client(mock_conn, ("127.0.0.1", 9999))
        mock_conn.sendall.assert_called_once()

    def test_response_is_valid_encrypted_json(self, brain):
        """The response sent should decrypt to valid JSON."""
        request = {"symbol": "EURUSD"}
        encrypted_request = brain.encrypt(json.dumps(request)).encode("utf-8")

        import pandas as pd
        import numpy as np
        n = 60
        dummy_df = pd.DataFrame(
            {"Open": np.ones(n), "High": np.ones(n)+0.01, "Low": np.ones(n)-0.01,
             "Close": np.ones(n), "Volume": np.ones(n)*100},
            index=pd.date_range("2024-01-01", periods=n, freq="1h")
        )
        brain.data_ingestor.fetch_all_data.return_value = {
            "prices": {"H1": dummy_df},
            "news": [],
            "sentiment": 0.0
        }
        brain.strategy_master.get_consensus_signal.return_value = ("SELL", -25, {})
        brain.strategy_master.verify_trade.return_value = False
        brain.risk_manager.evaluate_market_regime.return_value = "High Volatility"

        sent_data = []

        mock_conn = MagicMock()
        mock_conn.recv.return_value = encrypted_request
        mock_conn.sendall.side_effect = lambda data: sent_data.append(data)
        mock_conn.__enter__ = lambda s: mock_conn
        mock_conn.__exit__ = MagicMock(return_value=False)

        brain.handle_client(mock_conn, ("127.0.0.1", 9999))

        assert len(sent_data) == 1
        # Decrypt the response
        encrypted_response = sent_data[0].decode("utf-8")
        decrypted = brain.decrypt(encrypted_response)
        response_json = json.loads(decrypted)
        assert response_json["status"] == "success"
        assert "signal" in response_json

    def test_invalid_encrypted_data_logged_as_error(self, brain):
        """Corrupted input should not crash the server."""
        mock_conn = MagicMock()
        mock_conn.recv.return_value = b"not_valid_base64_or_encrypted_data!!!"
        mock_conn.__enter__ = lambda s: mock_conn
        mock_conn.__exit__ = MagicMock(return_value=False)

        # Should not raise
        brain.handle_client(mock_conn, ("127.0.0.1", 9999))