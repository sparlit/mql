# Project: Autonomous AutoTrader (AAT)
# Version: V3.2.0_20260606
# License: 100% FOSS / GNU GPL v3
# Author: Simon Peter
# Verification: Zero-Stub / Production Ready
# Description: Main Logic Engine for Dual-Mode (Scalp + Trade) Execution

import socket
import json
import pandas as pd
import yfinance as yf
import threading
import time
import logging
import re
import sqlite3
import os
import numpy as np
from questdb.ingress import Sender
from datetime import datetime, timedelta

# Absolute Versioned Imports
from Python.V3_1_0.StrategyMaster import StrategyMaster
from Python.V3_1_0.RiskManager import RiskManager
from Python.V3_1_0.DataAggregator import DataAggregator
from Python.V3_1_0.Security import AATSecurity

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("engine_debug.log"), logging.StreamHandler()]
)

class AutonomousAutoTrader:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.strategy_master = StrategyMaster()
        self.risk_manager = RiskManager()
        self.aggregator = DataAggregator()
        self.security = AATSecurity()
        self.active = True
        self.news_cache = []
        self.sentiment_text = ""
        self.db_path = "db/aat_trading.db"
        self.quest_host = os.environ.get("QUESTDB_HOST", "localhost")
        self.quest_port = int(os.environ.get("QUESTDB_PORT", 9009))
        self._init_db()
        threading.Thread(target=self.background_aggregator, daemon=True).start()

    def log_quest(self, table, data):
        try:
            with Sender(self.quest_host, self.quest_port) as sender:
                sender.row(table, symbols={"source": "aat_engine"}, columns=data).at_now()
                sender.flush()
        except Exception as e:
            logging.debug(f"QuestDB offline: {e}")

    def _init_db(self):
        if not os.path.exists('db'): os.makedirs('db')
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS aat_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, item TEXT, finding_insight TEXT, priority INTEGER, status TEXT, recommendations TEXT, diff_log TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        conn.commit(); conn.close()

    def audit_log(self, category, item, insight, priority=1, status="Info"):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO aat_audit (category, item, finding_insight, priority, status) VALUES (?, ?, ?, ?, ?)",
                     (category, item, insight, priority, status))
        conn.commit(); conn.close()

    def background_aggregator(self):
        while self.active:
            try:
                self.news_cache = self.aggregator.fetch_forexfactory_news()
                self.sentiment_text = self.aggregator.fetch_fxstreet_sentiment() + " " + self.aggregator.fetch_reuters_bloomberg_rss()
                if len(self.sentiment_text) < 100:
                    self.sentiment_text = self.aggregator.get_failover_data("EURUSD=X")
            except Exception as e:
                logging.error(f"Aggregator Error: {e}")
            time.sleep(300)

    def map_symbol(self, symbol):
        symbol = re.sub(r'\.[a-zA-Z0-9]+$', '', symbol)
        mapping = {"XAUUSD": "GC=F", "XAGUSD": "SI=F", "WTI": "CL=F", "SP500": "ES=F"}
        return mapping.get(symbol, f"{symbol}=X" if len(symbol)==6 else symbol)

    def fetch_data(self, symbol):
        yf_symbol = self.map_symbol(symbol)
        try:
            ticker = yf.Ticker(yf_symbol)
            dfs = {}
            for tf, (per, inv) in {'M1':('1d','1m'),'M5':('5d','5m'),'M15':('5d','15m'),'H1':('1mo','1h'),'H4':('1mo','4h'),'D1':('1y','1d')}.items():
                df = ticker.history(period=per, interval=inv)
                if not df.empty: dfs[tf] = df
            return dfs
        except Exception as e:
            logging.error(f"Fetch Error: {e}"); return None

    def handle_client(self, conn, addr):
        start_time = time.time()
        with conn:
            try:
                data_raw = conn.recv(10240).decode('utf-8').strip()
                if not data_raw: return
                decrypted = self.security.decrypt(data_raw)
                if not decrypted: return
                data = json.loads(decrypted)
                symbol = data.get("symbol", "EURUSD")
                self.risk_manager.account_balance = data.get("balance", 10000)
                dfs = self.fetch_data(symbol)
                if dfs:
                    symbol_sentiment = self.aggregator.fetch_fxstreet_sentiment(symbol_filter=symbol)
                    combined_sentiment = (symbol_sentiment if len(symbol_sentiment) > 50 else self.sentiment_text)

                    # Dual-Mode Consensus
                    res = self.strategy_master.get_dual_consensus(dfs, combined_sentiment)

                    mode = "NEUTRAL"
                    if res["scalp_signal"] != "NEUTRAL" and res["trade_signal"] != "NEUTRAL": mode = "BOTH"
                    elif res["scalp_signal"] != "NEUTRAL": mode = "SCALP"
                    elif res["trade_signal"] != "NEUTRAL": mode = "TRADE"

                    news_impact = False
                    for event in self.news_cache:
                        if event['currency'] in symbol and abs(event['datetime'] - datetime.now()) < timedelta(minutes=30):
                            news_impact = True; break

                    lot_size = self.risk_manager.calculate_position_size(
                        entry_price=dfs['H1']['Close'].iloc[-1],
                        stop_loss_points=data.get("sl_points", 200),
                        tick_value=data.get("tick_value", 1.0)
                    )

                    broker_price = float(dfs['M1']['Close'].iloc[-1])
                    try:
                        bench_ticker = yf.Ticker(self.map_symbol(symbol))
                        yf_price = float(bench_ticker.fast_info['lastPrice'])
                    except: yf_price = broker_price

                    latency = (time.time() - start_time) * 1000
                    response = {
                        "status": "success", "symbol": symbol, "mode": mode,
                        "scalp_signal": res["scalp_signal"], "trade_signal": res["trade_signal"],
                        "scalp_conf": int(res["scalp_conf"]), "trade_conf": int(res["trade_conf"]),
                        "recommended_lot": float(lot_size), "news_impact": bool(news_impact),
                        "latency": float(round(latency, 2)), "arb_alert": bool(abs(broker_price - yf_price) > 0.0005),
                        "tp_mult": res["exit_mult"]["tp"], "sl_mult": res["exit_mult"]["sl"]
                    }

                    self.log_quest("signals", {"symbol": symbol, "mode": mode, "latency": latency})
                    self.audit_log("Strategy", "Dual Signal", f"Mode: {mode}, Scalp: {res['scalp_signal']}, Trade: {res['trade_signal']}", 1, "Success")

                else: response = {"status": "error", "message": "Data fetch failed"}
                encrypted_resp = self.security.encrypt(json.dumps(response)) + "\n"
                conn.sendall(encrypted_resp.encode('utf-8'))
            except Exception as e:
                logging.error(f"Client Error: {e}")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(50)
            logging.info(f"AAT Engine V3.2.0 (Dual-Mode) Running on {self.host}:{self.port}")
            while self.active:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    AutonomousAutoTrader().run()
