import socket
import json
import pandas as pd
import yfinance as yf
import threading
import time
import logging
import re
from datetime import datetime, timedelta
from AAT_StrategyMaster_V1_0_0 import StrategyMaster
from AAT_RiskManager_V1_0_0 import RiskManager
from AAT_DataAggregator_V1_0_0 import DataAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("engine_debug.log"),
        logging.StreamHandler()
    ]
)

class AutonomousAutoTrader:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.strategy_master = StrategyMaster()
        self.risk_manager = RiskManager()
        self.aggregator = DataAggregator()
        self.active = True
        self.cache = {}
        self.all_dfs = {}

        self.news_cache = []
        self.sentiment_cache = "Neutral"
        self.poly_cache = "Neutral"

        logging.info(f"Autonomous AutoTrader Engine (TCP) started on {host}:{port}")
        threading.Thread(target=self.background_aggregator, daemon=True).start()

    def background_aggregator(self):
        while self.active:
            try:
                self.news_cache = self.aggregator.fetch_forexfactory_news()
                self.sentiment_cache = self.aggregator.fetch_fxstreet_sentiment()
                self.poly_cache = self.aggregator.fetch_polymarket_sentiment()
                logging.info("Background aggregator updated.")
            except Exception as e:
                logging.error(f"Background aggregator error: {e}")
            time.sleep(300)

    def map_symbol(self, symbol):
        symbol = re.sub(r'\.[a-zA-Z0-9]+$', '', symbol)
        mapping = {
            "XAUUSD": "GC=F", "XAGUSD": "SI=F", "GOLD": "GC=F", "SILVER": "SI=F",
            "WTI": "CL=F", "BRENT": "BZ=F", "US30": "YM=F", "NAS100": "NQ=F",
            "SP500": "ES=F", "BTCUSD": "BTC-USD", "ETHUSD": "ETH-USD"
        }
        if symbol in mapping: return mapping[symbol]
        if len(symbol) == 6 and symbol.isupper(): return f"{symbol}=X"
        return symbol

    def fetch_data(self, symbol):
        yf_symbol = self.map_symbol(symbol)
        try:
            ticker = yf.Ticker(yf_symbol)
            dfs = {}
            intervals = {
                'M1': ('1d', '1m'), 'M5': ('5d', '5m'), 'M15': ('5d', '15m'),
                'M30': ('5d', '30m'), 'H1': ('1mo', '1h'), 'H4': ('3mo', '1h'),
                'D1': ('1y', '1d'), 'W1': ('2y', '1wk'), 'MN': ('max', '1mo')
            }
            for tf, (period, interval) in intervals.items():
                cache_key = f"{symbol}_{tf}"
                if cache_key in self.cache:
                    last_fetch, cached_df = self.cache[cache_key]
                    if time.time() - last_fetch < 60:
                        dfs[tf] = cached_df
                        continue
                df = ticker.history(period=period, interval=interval)
                if df.empty: continue
                if tf == 'H4' and interval == '1h':
                    df = df.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
                self.cache[cache_key] = (time.time(), df)
                dfs[tf] = df
            if any(not df.empty for df in dfs.values()):
                self.all_dfs[symbol] = dfs
                return dfs
            return None
        except Exception as e:
            logging.error(f"Error fetching data for {yf_symbol}: {e}")
            return None

    def handle_client(self, conn, addr):
        with conn:
            try:
                conn.settimeout(5.0)
                # Security: Payload Size Limit (10KB)
                data_raw = ""
                while len(data_raw) < 10240:
                    chunk = conn.recv(1024).decode('utf-8')
                    if not chunk: break
                    data_raw += chunk
                    if data_raw.endswith('}'): break

                if not data_raw or not data_raw.strip().startswith('{'): return

                # Security: Strict Schema Validation
                try:
                    data = json.loads(data_raw)
                    if "symbol" not in data: raise ValueError("Missing symbol")
                except Exception as e:
                    logging.warning(f"Invalid payload from {addr}: {e}")
                    return

                symbol = data.get("symbol", "EURUSD")
                balance = data.get("balance", 10000)
                tick_value = data.get("tick_value", 1.0)
                sl_points = data.get("sl_points", 200)
                current_profit_pips = data.get("current_profit_pips", 0)

                self.risk_manager.account_balance = balance
                dfs = self.fetch_data(symbol)

                if dfs is not None:
                    h1_df = dfs.get('H1')
                    trend = self.analyze_trend(h1_df)
                    signal, confidence, tf_results = self.strategy_master.get_consensus_signal(dfs)
                    regime = self.risk_manager.evaluate_market_regime(h1_df)

                    news_impact = False
                    now = datetime.now()
                    for event in self.news_cache:
                        if event['currency'] in symbol and abs(event['datetime'] - now) < timedelta(minutes=30):
                            news_impact = True
                            break

                    if self.sentiment_cache == "Bullish" and signal == "BUY": confidence += 5
                    if self.poly_cache == "Hawkish" and "USD" in symbol[:3]: confidence += 5

                    is_verified = abs(confidence) >= 15
                    lot_size = self.risk_manager.calculate_position_size(
                        entry_price=h1_df['Close'].iloc[-1] if h1_df is not None else 0,
                        stop_loss_points=sl_points, tick_value=tick_value,
                        is_pyramid=(current_profit_pips > 0), current_profit_pips=current_profit_pips
                    )

                    var_val = self.risk_manager.calculate_var(h1_df)
                    corr_val = self.risk_manager.calculate_correlation(self.all_dfs)

                    response = {
                        "status": "success", "symbol": symbol, "trend": trend, "signal": signal,
                        "confidence": int(confidence), "regime": regime, "verified": is_verified,
                        "recommended_lot": lot_size, "news_impact": news_impact,
                        "var": round(var_val, 4), "correlation": round(corr_val, 2),
                        "polymarket": self.poly_cache, "timestamp": datetime.now().isoformat()
                    }
                    for tf, score in tf_results.items(): response[tf] = int(score)
                else:
                    response = {"status": "error", "message": f"Data fetch failed for {symbol}"}
                conn.sendall(json.dumps(response).encode('utf-8'))
            except Exception as e:
                logging.error(f"Error processing request from {addr}: {e}")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Security: Bind only to localhost
            s.bind((self.host, self.port))
            s.listen(50)
            logging.info(f"Listening on {self.host}:{self.port}...")
            while self.active:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def analyze_trend(self, df):
        if df is None or len(df) < 50: return "Neutral"
        curr = df['Close'].iloc[-1]
        sma = df['Close'].rolling(window=200).mean().iloc[-1]
        if pd.isna(sma): sma = df['Close'].mean()
        return "Bullish" if curr > sma else ("Bearish" if curr < sma else "Neutral")

if __name__ == "__main__":
    AutonomousAutoTrader().run()
