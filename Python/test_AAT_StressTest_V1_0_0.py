import pytest
from unittest.mock import patch, MagicMock
import socket
from AAT_StressTest_V1_0_0 import simulate_client
from AAT_Security_V1_0_0 import AATSecurity

def test_simulate_client_success():
    security = AATSecurity()
    with patch('socket.socket') as mock_socket:
        mock_sock_inst = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_inst

        # Mock receive data (valid encrypted JSON ending with })
        response_json = '{"status": "success", "verified": true, "recommended_lot": 0.01}'
        encrypted_response = security.encrypt(response_json).encode('utf-8')
        mock_sock_inst.recv.side_effect = [encrypted_response, b""]

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
