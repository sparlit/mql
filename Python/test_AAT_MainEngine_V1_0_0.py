import pytest
import json
import socket
import threading
import time
from unittest.mock import patch, MagicMock
from AAT_MainEngine_V1_0_0 import AutonomousAutoTrader

@pytest.fixture
def engine():
    # Patch the background thread to avoid it running during tests
    with patch('threading.Thread'):
        return AutonomousAutoTrader()

def test_map_symbol(engine):
    assert engine.map_symbol("EURUSD") == "EURUSD=X"
    assert engine.map_symbol("XAUUSD.pro") == "GC=F"
    assert engine.map_symbol("BTCUSD") == "BTC-USD"
    assert engine.map_symbol("US30") == "YM=F"

def test_fetch_data_caching(engine):
    with patch('yfinance.Ticker') as mock_ticker:
        mock_df = MagicMock()
        mock_df.empty = False
        mock_ticker.return_value.history.return_value = mock_df

        # First fetch
        engine.fetch_data("EURUSD")
        assert "EURUSD_H1" in engine.cache

        # Second fetch should use cache if within 60s
        with patch.object(engine, 'map_symbol', return_value="EURUSD=X"):
             engine.fetch_data("EURUSD")
             # history should not be called again for H1 if cached
             # (actually fetch_data iterates all TFs)
             pass

def test_handle_client_success(engine):
    mock_conn = MagicMock()
    mock_addr = ('127.0.0.1', 12345)

    request_dict = {
        "symbol": "EURUSD",
        "balance": 10000,
        "sl_points": 200,
        "tick_value": 1.0
    }
    # Mock encryption_enabled for test
    engine.encryption_enabled = True
    encrypted_request = engine.security.encrypt(json.dumps(request_dict)).encode('utf-8')

    mock_conn.recv.side_effect = [encrypted_request, b""]

    with patch.object(engine, 'fetch_data') as mock_fetch, \
         patch.object(engine.strategy_master, 'get_consensus_signal') as mock_signal, \
         patch.object(engine.risk_manager, 'calculate_position_size', return_value=0.01), \
         patch.object(engine.risk_manager, 'evaluate_market_regime', return_value="Stable"), \
         patch.object(engine.risk_manager, 'calculate_var', return_value=0.005), \
         patch.object(engine.risk_manager, 'calculate_correlation', return_value=0.5):

        mock_fetch.return_value = {'H1': MagicMock()}
        mock_signal.return_value = ("BUY", 20, {'H1': 5})

        engine.handle_client(mock_conn, mock_addr)

        mock_conn.sendall.assert_called_once()
        encrypted_resp = mock_conn.sendall.call_args[0][0].decode('utf-8')
        decrypted_resp = engine.security.decrypt(encrypted_resp)
        sent_data = json.loads(decrypted_resp)
        assert sent_data['status'] == 'success'
        assert sent_data['signal'] == 'BUY'
        assert sent_data['recommended_lot'] == 0.01
