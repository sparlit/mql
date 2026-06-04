import socket
import json
import pandas as pd
import yfinance as yf
import threading
import time
from datetime import datetime
from strategy_master import StrategyMaster
from risk_manager import RiskManager

class AutonomousAutoTrader:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.strategy_master = StrategyMaster()
        self.risk_manager = RiskManager()
        self.active = True
        self.cache = {}
        print(f"Autonomous AutoTrader Engine (TCP) started on {host}:{port}")

    def fetch_data(self, symbol):
        # Symbol mapping for Forex
        if len(symbol) == 6 and symbol.isupper():
            yf_symbol = symbol + "=X"
        else:
            yf_symbol = symbol

        try:
            ticker = yf.Ticker(yf_symbol)
            dfs = {}
            # Fetch All Timeframes
            intervals = {
                'M1': ('1d', '1m'),
                'M5': ('5d', '5m'),
                'M15': ('5d', '15m'),
                'M30': ('5d', '30m'),
                'H1': ('1mo', '1h'),
                'H4': ('3mo', '1h'), # yfinance doesn't have 4h, using 1h and will resample
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
                if not df.empty:
                    if tf == 'H4':
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
            print(f"Error fetching data for {yf_symbol}: {e}")
            return None

    def handle_client(self, conn, addr):
        with conn:
            try:
                data_raw = conn.recv(1024).decode('utf-8')
                if not data_raw:
                    return

                data = json.loads(data_raw)
                symbol = data.get("symbol", "EURUSD")
                balance = data.get("balance", 10000)
                self.risk_manager.account_balance = balance

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Request: {symbol} | Balance: {balance}")

                dfs = self.fetch_data(symbol)
                if dfs is not None:
                    # Analyze based on H1 trend
                    trend = self.analyze_trend(dfs.get('H1'))
                    signal, confidence, tf_results = self.strategy_master.get_consensus_signal(dfs)
                    regime = self.risk_manager.evaluate_market_regime(dfs.get('H1'))

                    # Logic: 100% autonomous requires high confidence and stable regime
                    # If high volatility, we require even higher confidence
                    threshold = 15
                    if "High Volatility" in regime:
                        threshold = 25

                    is_verified = abs(confidence) >= threshold

                    response = {
                        "status": "success",
                        "symbol": symbol,
                        "trend": trend,
                        "signal": signal,
                        "confidence": int(confidence),
                        "regime": regime,
                        "verified": is_verified,
                        "timestamp": datetime.now().isoformat()
                    }
                    # Flatten tf_results into the main response for easier MQL5 parsing
                    for tf, score in tf_results.items():
                        response[tf] = int(score)
                else:
                    response = {"status": "error", "message": "Data fetch failed"}

                conn.sendall(json.dumps(response).encode('utf-8'))
            except Exception as e:
                print(f"Error processing client request: {e}")
                error_resp = {"status": "error", "message": str(e)}
                try:
                    conn.sendall(json.dumps(error_resp).encode('utf-8'))
                except:
                    pass

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print("Autonomous Loop active. Listening for MT5 signals...")
            while self.active:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()

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
