import pytest
from unittest.mock import patch, MagicMock
import socket
from AAT_StressTest_V1_0_0 import simulate_client

def test_simulate_client_success():
    with patch('socket.socket') as mock_socket:
        mock_sock_inst = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_inst

        # Mock receive data (valid JSON ending with })
        mock_sock_inst.recv.return_value = b'{"status": "success", "verified": true, "recommended_lot": 0.01}'

        # Should not raise any exception
        simulate_client(1, "EURUSD")

        mock_sock_inst.connect.assert_called_with(('127.0.0.1', 5555))
        mock_sock_inst.sendall.assert_called()

def test_simulate_client_connection_error():
    with patch('socket.socket') as mock_socket:
        mock_sock_inst = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_inst
        mock_sock_inst.connect.side_effect = ConnectionRefusedError()

        # Should handle connection error gracefully
        simulate_client(1, "EURUSD")
