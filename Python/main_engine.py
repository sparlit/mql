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
        print(f"Autonomous AutoTrader Engine (TCP) started on {host}:{port}")

    def fetch_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1mo", interval="1h")
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def handle_client(self, conn, addr):
        with conn:
            data_raw = conn.recv(1024).decode('utf-8')
            if not data_raw:
                return

            try:
                data = json.loads(data_raw)
                symbol = data.get("symbol", "EURUSD")
                balance = data.get("balance", 10000)
                self.risk_manager.account_balance = balance

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Request: {symbol} | Balance: {balance}")

                df = self.fetch_data(symbol)
                if df is not None:
                    trend = self.analyze_trend(df)
                    signal, confidence = self.strategy_master.get_consensus_signal(df)
                    regime = self.risk_manager.evaluate_market_regime(df)

                    # Logic: 100% autonomous requires high confidence
                    is_verified = abs(confidence) >= 2

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
                else:
                    response = {"status": "error", "message": "Data fetch failed"}

                conn.sendall(json.dumps(response).encode('utf-8'))
            except Exception as e:
                print(f"Error processing client request: {e}")
                error_resp = {"status": "error", "message": str(e)}
                conn.sendall(json.dumps(error_resp).encode('utf-8'))

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
