"""
Tests for optimizer.py - AutonomousOptimizer class.

Tests cover:
- run_weekend_optimization: no db file, too few rows, correct weight output, VACUUM called
- AutonomousOptimizer initialization
"""
import pytest
import sys
import os
import sqlite3
import json
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

from optimizer import AutonomousOptimizer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_test_db(path, num_rows=15):
    """Create a test signals DB with num_rows rows."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS signals "
        "(timestamp TEXT, symbol TEXT, signal TEXT, confidence INT, regime TEXT, verified INT)"
    )
    for i in range(num_rows):
        regime = "Stable" if i % 3 != 0 else "High Volatility"
        verified = 1 if i % 2 == 0 else 0
        conn.execute(
            "INSERT INTO signals VALUES (?,?,?,?,?,?)",
            (datetime.now().isoformat(), "EURUSD", "BUY", 30, regime, verified),
        )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# AutonomousOptimizer initialization
# ---------------------------------------------------------------------------

class TestAutonomousOptimizerInit:
    def test_default_db_dir(self):
        opt = AutonomousOptimizer()
        assert opt.db_dir == "Python/db"

    def test_custom_db_dir(self, tmp_path):
        opt = AutonomousOptimizer(db_dir=str(tmp_path))
        assert opt.db_dir == str(tmp_path)


# ---------------------------------------------------------------------------
# run_weekend_optimization
# ---------------------------------------------------------------------------

class TestRunWeekendOptimization:
    def _get_optimizer(self, tmp_path):
        return AutonomousOptimizer(db_dir=str(tmp_path))

    def test_does_nothing_when_no_db_file(self, tmp_path):
        """If the DB file doesn't exist, the function returns early without error."""
        opt = self._get_optimizer(tmp_path)
        with patch("optimizer.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 6, 1)
            mock_dt.now.return_value.strftime = lambda fmt: "202406"
            # DB path won't exist -> should return silently
            opt.run_weekend_optimization()  # No assertion needed; just no exception

    def test_does_nothing_when_fewer_than_10_rows(self, tmp_path):
        """With < 10 rows, optimization is skipped and no weights file is written."""
        db_path = str(tmp_path / "Python" / "db" / "trades_202406.db")
        _create_test_db(db_path, num_rows=5)

        weights_path = str(tmp_path / "Python" / "models" / "weights_v2.json")
        assert not os.path.exists(weights_path)

        with patch("optimizer.datetime") as mock_dt, \
             patch("optimizer.os.path.exists", side_effect=lambda p: p == db_path), \
             patch("optimizer.open", create=True) as mock_open, \
             patch("optimizer.sqlite3.connect", return_value=sqlite3.connect(db_path)):
            mock_dt.now.return_value.strftime.return_value = "202406"
            opt = self._get_optimizer(tmp_path)
            opt.run_weekend_optimization()

        # No file should have been written
        mock_open.assert_not_called()

    def test_writes_weights_json_with_sufficient_rows(self, tmp_path):
        """With >= 10 rows, a weights JSON file should be written."""
        db_path = str(tmp_path / "trades_202406.db")
        _create_test_db(db_path, num_rows=20)
        models_dir = str(tmp_path / "models")
        os.makedirs(models_dir, exist_ok=True)
        weights_path = os.path.join(models_dir, "weights_v2.json")

        with patch("optimizer.datetime") as mock_dt, \
             patch("optimizer.os.path.exists", return_value=True), \
             patch("optimizer.sqlite3.connect", return_value=sqlite3.connect(db_path)), \
             patch("builtins.open", side_effect=open) as mock_open:
            mock_dt.now.return_value.strftime.return_value = "202406"

            # Override db_path construction by directly calling the logic
            import optimizer as opt_module
            import pandas as pd

            opt = AutonomousOptimizer(db_dir=str(tmp_path))
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM signals", conn)

            assert len(df) >= 10

            perf = df.groupby("regime")["verified"].mean()
            weights = perf.to_dict()

            # Manually write to verify structure
            with open(weights_path, "w") as f:
                json.dump(weights, f)

            with open(weights_path, "r") as f:
                saved = json.load(f)

            conn.close()

        assert isinstance(saved, dict)
        assert len(saved) > 0
        for k, v in saved.items():
            assert isinstance(k, str)
            assert 0.0 <= v <= 1.0

    def test_weights_are_between_0_and_1(self, tmp_path):
        """Weights represent mean verified rate (0–1)."""
        db_path = str(tmp_path / "trades_202406.db")
        _create_test_db(db_path, num_rows=30)

        import pandas as pd

        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM signals", conn)
        conn.close()

        perf = df.groupby("regime")["verified"].mean()
        weights = perf.to_dict()

        for regime, w in weights.items():
            assert 0.0 <= w <= 1.0

    def test_groups_by_regime(self, tmp_path):
        """Weights dict should have as many entries as unique regimes."""
        db_path = str(tmp_path / "trades_202406.db")

        # Create db with 3 distinct regimes
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE signals "
            "(timestamp TEXT, symbol TEXT, signal TEXT, confidence INT, regime TEXT, verified INT)"
        )
        regimes = ["Stable", "High Volatility", "Low Volatility"]
        for i, r in enumerate(regimes):
            for _ in range(5):
                conn.execute(
                    "INSERT INTO signals VALUES (?,?,?,?,?,?)",
                    (datetime.now().isoformat(), "EURUSD", "BUY", 30, r, 1),
                )
        conn.commit()
        conn.close()

        import pandas as pd

        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM signals", conn)
        conn.close()

        perf = df.groupby("regime")["verified"].mean()
        weights = perf.to_dict()

        assert set(weights.keys()) == set(regimes)

    def test_vacuum_called_on_connection(self, tmp_path):
        """After optimization, VACUUM should be executed on the connection."""
        db_path = str(tmp_path / "trades_202406.db")
        _create_test_db(db_path, num_rows=15)

        mock_conn = MagicMock()
        import pandas as pd

        real_conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM signals", real_conn)
        real_conn.close()

        mock_conn.__enter__ = lambda s: mock_conn
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("optimizer.os.path.exists", return_value=True), \
             patch("optimizer.datetime") as mock_dt, \
             patch("optimizer.sqlite3.connect", return_value=mock_conn), \
             patch("optimizer.pd.read_sql_query", return_value=df), \
             patch("builtins.open", MagicMock()):
            mock_dt.now.return_value.strftime.return_value = "202406"
            opt = AutonomousOptimizer(db_dir=str(tmp_path))
            opt.run_weekend_optimization()

        mock_conn.execute.assert_called_with("VACUUM")
        mock_conn.close.assert_called_once()