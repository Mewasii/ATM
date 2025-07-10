import pandas as pd
import asyncio
import threading
from datetime import datetime, timedelta
from binance.client import Client
from utils.config import Config
from agents.websocket_agent import WebSocketAgent
from filelock import FileLock
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalDataAgent:
    def __init__(self, symbol="BTCUSDT", interval="1h", data_dir="data/raw"):
        """
        Initialize HistoricalDataAgent for fetching and updating kline data.
        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            interval: Kline interval (e.g., "1h", "1d")
            data_dir: Directory to store data files
        """
        self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)
        self.symbol = symbol
        self.interval = interval
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, f"{symbol}_{interval}.csv")
        self.websocket_agent = None
        self.websocket_thread = None
        self.running = False
        os.makedirs(data_dir, exist_ok=True)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(Exception)
    )
    def fetch_historical_klines(self, start_date, end_date, limit=1000):
        """
        Fetch historical kline data from Binance API.
        Args:
            start_date: Start datetime
            end_date: End datetime
            limit: Number of klines per request (max 1000)
        Returns:
            pandas.DataFrame: Kline data
        """
        logger.info(f"Fetching klines from {start_date} to {end_date}")
        klines = self.client.get_klines(
            symbol=self.symbol,
            interval=self.interval,
            startTime=int(start_date.timestamp() * 1000),
            endTime=int(end_date.timestamp() * 1000),
            limit=limit
        )
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].astype(float)
        return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]

    def collect_historical_data(self, start_date="2019-01-01"):
        """
        Collect historical data from start_date to current time and save to CSV.
        Args:
            start_date: Start date for data collection (default: 2019-01-01)
        """
        start_dt = pd.to_datetime(start_date)
        end_dt = datetime.utcnow()
        interval_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
        interval_minutes = interval_map.get(self.interval, 60)
        step = timedelta(minutes=interval_minutes * 1000)

        all_data = []
        current_dt = start_dt
        while current_dt < end_dt:
            next_dt = min(current_dt + step, end_dt)
            try:
                df = self.fetch_historical_klines(current_dt, next_dt)
                if not df.empty:
                    all_data.append(df)
                current_dt = next_dt
            except Exception as e:
                logger.error(f"Error fetching data for {current_dt} to {next_dt}: {e}")
                break

        if all_data:
            full_df = pd.concat(all_data).drop_duplicates(subset=['open_time']).sort_values('open_time')
            self.save_to_csv(full_df)
            logger.info(f"Saved historical data to {self.data_file}")

    def save_to_csv(self, df):
        """
        Save DataFrame to CSV with file locking to prevent conflicts.
        Args:
            df: DataFrame to save
        """
        lock = FileLock(f"{self.data_file}.lock")
        with lock:
            df.to_csv(self.data_file, index=False)
            logger.info(f"Data saved to {self.data_file}")

    def append_to_csv(self, df):
        """
        Append new data to existing CSV with file locking.
        Args:
            df: DataFrame with new data
        """
        lock = FileLock(f"{self.data_file}.lock")
        with lock:
            if os.path.exists(self.data_file):
                existing_df = pd.read_csv(self.data_file, parse_dates=['open_time'])
                combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['open_time'], keep='last')
                combined_df = combined_df.sort_values('open_time')
            else:
                combined_df = df
            combined_df.to_csv(self.data_file, index=False)
            logger.info(f"Appended new data to {self.data_file}")

    def read_data(self):
        """
        Read data from CSV file.
        Returns:
            pandas.DataFrame: Data from CSV
        """
        if os.path.exists(self.data_file):
            return pd.read_csv(self.data_file, parse_dates=['open_time'])
        return pd.DataFrame(columns=['open_time', 'open', 'high', 'low', 'close', 'volume'])

    def start_websocket(self):
        """
        Start WebSocket to collect real-time kline data.
        """
        if self.websocket_agent and self.running:
            self.stop_websocket()

        self.websocket_agent = WebSocketAgent(self.symbol, self.interval)
        self.running = True
        self.websocket_thread = threading.Thread(
            target=lambda: asyncio.run(self.websocket_agent.connect()),
            daemon=True
        )
        self.websocket_thread.start()

        # Start a separate thread to periodically append WebSocket data
        threading.Thread(
            target=self._websocket_data_handler,
            daemon=True
        ).start()
        logger.info("Started WebSocket for real-time updates")

    def stop_websocket(self):
        """
        Stop WebSocket and clean up.
        """
        if self.websocket_agent:
            self.websocket_agent.stop()
            self.running = False
            if self.websocket_thread:
                self.websocket_thread.join(timeout=5)
            self.websocket_agent = None
            self.websocket_thread = None
        logger.info("Stopped WebSocket")

    def _websocket_data_handler(self):
        """
        Periodically check WebSocket data and append to CSV.
        """
        while self.running:
            try:
                ws_df = self.websocket_agent.get_data()
                if not ws_df.empty:
                    self.append_to_csv(ws_df)
            except Exception as e:
                logger.error(f"Error handling WebSocket data: {e}")
            time.sleep(60)  # Check every 60 seconds

    def set_symbol(self, symbol):
        """
        Update the trading pair symbol and restart WebSocket if running.
        """
        self.symbol = symbol
        self.data_file = os.path.join(self.data_dir, f"{self.symbol}_{self.interval}.csv")
        if self.websocket_agent:
            self.stop_websocket()
            self.start_websocket()

    def set_interval(self, interval):
        """
        Update the interval and restart WebSocket if running.
        """
        self.interval = interval
        self.data_file = os.path.join(self.data_dir, f"{self.symbol}_{self.interval}.csv")
        if self.websocket_agent:
            self.stop_websocket()
            self.start_websocket()