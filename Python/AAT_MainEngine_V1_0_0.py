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
from datetime import datetime, timedelta
from AAT_StrategyMaster_V1_0_0 import StrategyMaster
from AAT_RiskManager_V1_0_0 import RiskManager
from AAT_DataAggregator_V1_0_0 import DataAggregator
from AAT_Security_V1_0_0 import AATSecurity

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
        self.cache = {}
        self.news_cache = []
        self.sentiment_text = ""
        self.db_path = "db/aat_trading.db"
        self._init_db()
        threading.Thread(target=self.background_aggregator, daemon=True).start()

    def _init_db(self):
        if not os.path.exists('db'): os.makedirs('db')
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, level TEXT, message TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS trades (timestamp TEXT, symbol TEXT, signal TEXT, confidence REAL, status TEXT)")
        conn.commit()
        conn.close()

    def log_to_db(self, level, message):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO logs VALUES (?, ?, ?)", (datetime.now().isoformat(), level, message))
        conn.commit()
        conn.close()

    def background_aggregator(self):
        while self.active:
            try:
                self.news_cache = self.aggregator.fetch_forexfactory_news()
                self.sentiment_text = self.aggregator.fetch_fxstreet_sentiment() + " " + self.aggregator.fetch_reuters_bloomberg_rss()
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
            for tf, (per, inv) in {'M1':('1d','1m'),'M5':('5d','5m'),'H1':('1mo','1h'),'D1':('1y','1d')}.items():
                df = ticker.history(period=per, interval=inv)
                if not df.empty: dfs[tf] = df
            return dfs
        except Exception as e:
            logging.error(f"Fetch Error: {e}")
            return None

    def handle_client(self, conn, addr):
        with conn:
            try:
                data_raw = conn.recv(10240).decode('utf-8').strip()
                if not data_raw: return

                # Decrypt
                decrypted = self.security.decrypt(data_raw)
                if not decrypted: return
                data = json.loads(decrypted)

                symbol = data.get("symbol", "EURUSD")
                self.risk_manager.account_balance = data.get("balance", 10000)
                dfs = self.fetch_data(symbol)

                if dfs:
                    signal, conf, tf_results = self.strategy_master.get_consensus_signal(dfs, self.sentiment_text)

                    news_impact = False
                    for event in self.news_cache:
                        if event['currency'] in symbol and abs(event['datetime'] - datetime.now()) < timedelta(minutes=30):
                            news_impact = True; break

                    lot_size = self.risk_manager.calculate_position_size(
                        entry_price=dfs['H1']['Close'].iloc[-1],
                        stop_loss_points=data.get("sl_points", 200),
                        tick_value=data.get("tick_value", 1.0),
                        is_pyramid=(data.get("current_profit_pips", 0) > 200),
                        current_profit_pips=data.get("current_profit_pips", 0)
                    )

                    response = {
                        "status": "success", "symbol": symbol, "signal": signal, "confidence": int(conf),
                        "verified": signal != "NEUTRAL", "recommended_lot": lot_size, "news_impact": news_impact,
                        "regime": self.risk_manager.evaluate_market_regime(dfs.get('H1')),
                        "var": round(self.risk_manager.calculate_var(dfs.get('H1')), 4),
                        "correlation": 0.0, "polymarket": "Neutral"
                    }
                    for tf, score in tf_results.items(): response[tf] = int(score)
                else: response = {"status": "error", "message": "Data fetch failed"}

                # Encrypt and Send
                encrypted_resp = self.security.encrypt(json.dumps(response)) + "\n"
                conn.sendall(encrypted_resp.encode('utf-8'))

            except Exception as e:
                logging.error(f"Client Error: {e}")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(50)
            logging.info(f"AAT Engine Running on {self.host}:{self.port}")
            while self.active:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    import os
    AutonomousAutoTrader().run()
