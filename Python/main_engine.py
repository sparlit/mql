import socket
import json
import pandas as pd
import yfinance as yf
import threading
import time
import logging
import re
from datetime import datetime
from strategy_master import StrategyMaster
from risk_manager import RiskManager

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
        self.active = True
        self.cache = {}
        logging.info(f"Autonomous AutoTrader Engine (TCP) started on {host}:{port}")

    def map_symbol(self, symbol):
        """
        Maps MT5 symbols to appropriate data provider tickers with dynamic suffix removal.
        """
        original_symbol = symbol
        # Remove common broker suffixes (e.g., EURUSD.pro -> EURUSD, GOLD.m -> GOLD)
        # Suffixes are usually .something or a single letter if the prefix is standard
        symbol = re.sub(r'\.[a-zA-Z0-9]+$', '', symbol)

        # Specific Mapping
        mapping = {
            "XAUUSD": "GC=F",
            "XAGUSD": "SI=F",
            "GOLD": "GC=F",
            "SILVER": "SI=F",
            "WTI": "CL=F",
            "BRENT": "BZ=F",
            "US30": "YM=F",
            "NAS100": "NQ=F",
            "SP500": "ES=F",
            "BTCUSD": "BTC-USD",
            "ETHUSD": "ETH-USD"
        }

        if symbol in mapping:
            return mapping[symbol]

        # Forex mapping
        if len(symbol) == 6 and symbol.isupper():
            return f"{symbol}=X"

        logging.warning(f"No specific mapping found for {original_symbol} (cleaned: {symbol}). Using as-is.")
        return symbol

    def fetch_data(self, symbol):
        """
        Fetches multi-timeframe data with robust fallback mechanisms and caching.
        """
        yf_symbol = self.map_symbol(symbol)

        try:
            ticker = yf.Ticker(yf_symbol)
            dfs = {}
            intervals = {
                'M1': ('1d', '1m'),
                'M5': ('5d', '5m'),
                'M15': ('5d', '15m'),
                'M30': ('5d', '30m'),
                'H1': ('1mo', '1h'),
                'H4': ('3mo', '1h'),
                'D1': ('1y', '1d'),
                'W1': ('2y', '1wk'),
                'MN': ('max', '1mo')
            }

            for tf, (period, interval) in intervals.items():
                cache_key = f"{symbol}_{tf}"
                if cache_key in self.cache:
                    last_fetch, cached_df = self.cache[cache_key]
                    if time.time() - last_fetch < 60: # 1 minute cache
                        dfs[tf] = cached_df
                        continue

                df = ticker.history(period=period, interval=interval)

                if df.empty:
                    logging.warning(f"Primary source empty for {yf_symbol} {tf}")
                    continue

                if tf == 'H4' and interval == '1h':
                    df = df.resample('4h').agg({
                        'Open': 'first',
                        'High': 'max',
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    }).dropna()

                self.cache[cache_key] = (time.time(), df)
                dfs[tf] = df

            return dfs if any(not df.empty for df in dfs.values()) else None
        except Exception as e:
            logging.error(f"Error fetching data for {yf_symbol}: {e}")
            return None

    def handle_client(self, conn, addr):
        with conn:
            try:
                conn.settimeout(10.0)
                data_raw = ""
                while True:
                    chunk = conn.recv(4096).decode('utf-8')
                    if not chunk: break
                    data_raw += chunk
                    if data_raw.endswith('}'): break # Basic JSON termination check

                if not data_raw:
                    return

                try:
                    data = json.loads(data_raw)
                except json.JSONDecodeError as e:
                    logging.error(f"Malformed JSON from {addr}: {e}")
                    return

                symbol = data.get("symbol", "EURUSD")
                balance = data.get("balance", 10000)
                tick_value = data.get("tick_value", 1.0)
                tick_size = data.get("tick_size", 0.00001)
                sl_points = data.get("sl_points", 200)

                self.risk_manager.account_balance = balance

                logging.info(f"Request from {addr}: {symbol} | Balance: {balance}")

                dfs = self.fetch_data(symbol)
                if dfs is not None:
                    h1_df = dfs.get('H1')
                    trend = self.analyze_trend(h1_df)
                    signal, confidence, tf_results = self.strategy_master.get_consensus_signal(dfs)
                    regime = self.risk_manager.evaluate_market_regime(h1_df)

                    # Multi-layer verification threshold
                    threshold = 15
                    if "High Volatility" in regime:
                        threshold = 25
                    if "Ranging" in regime:
                        threshold += 5

                    is_verified = abs(confidence) >= threshold

                    # Calculate position size in Python for cross-verification
                    lot_size = 0
                    if is_verified:
                        lot_size = self.risk_manager.calculate_position_size(
                            entry_price=h1_df['Close'].iloc[-1] if h1_df is not None else 0,
                            stop_loss_points=sl_points,
                            tick_value=tick_value
                        )

                    response = {
                        "status": "success",
                        "symbol": symbol,
                        "trend": trend,
                        "signal": signal,
                        "confidence": int(confidence),
                        "regime": regime,
                        "verified": is_verified,
                        "recommended_lot": lot_size,
                        "timestamp": datetime.now().isoformat()
                    }

                    for tf, score in tf_results.items():
                        response[tf] = int(score)
                else:
                    response = {"status": "error", "message": f"Data fetch failed for {symbol}"}

                conn.sendall(json.dumps(response).encode('utf-8'))
            except socket.timeout:
                logging.error(f"Timeout handling client {addr}")
            except Exception as e:
                logging.error(f"Error processing request from {addr}: {e}")
                error_resp = {"status": "error", "message": str(e)}
                try:
                    conn.sendall(json.dumps(error_resp).encode('utf-8'))
                except:
                    pass

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(5)
                logging.info(f"Listening on {self.host}:{self.port}...")
                while self.active:
                    conn, addr = s.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                    client_thread.daemon = True
                    client_thread.start()
        except Exception as e:
            logging.critical(f"Engine crash: {e}")

    def analyze_trend(self, df):
        if df is None or len(df) < 50: return "Neutral"
        current_price = df['Close'].iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        if pd.isna(sma200): sma200 = df['Close'].mean()

        if current_price > sma200: return "Bullish"
        elif current_price < sma200: return "Bearish"
        return "Neutral"

if __name__ == "__main__":
    trader = AutonomousAutoTrader()
    trader.run()
