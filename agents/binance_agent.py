import pandas as pd
from binance.client import Client
from utils.config import Config
from filelock import FileLock
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinanceAgent:
    def __init__(self):
        self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)
        self.symbol = Config.DEFAULT_SYMBOL
        self.interval = Config.DEFAULT_INTERVAL
        self.data_dir = Config.RAW_DATA_DIR
        self.data_file = os.path.join(self.data_dir, f"{self.symbol}_{self.interval}.csv")

    def fetch_klines(self, limit=1000):
        """
        Fetch historical kline data for the specified symbol and interval.
        Args:
            limit (int): Number of data points to fetch.
        Returns:
            pandas.DataFrame: Kline data with columns [open_time, open, high, low, close, volume].
        """
        logger.info(f"Fetching klines for {self.symbol} at {self.interval}")
        klines = self.client.get_klines(symbol=self.symbol, interval=self.interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].astype(float)
        df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
        self.save_to_csv(df)
        return df

    def save_to_csv(self, df):
        """
        Save DataFrame to CSV with file locking.
        Args:
            df: DataFrame to save.
        """
        os.makedirs(self.data_dir, exist_ok=True)
        lock = FileLock(f"{self.data_file}.lock")
        with lock:
            df.to_csv(self.data_file, index=False)
            logger.info(f"Saved data to {self.data_file}")

    def load_from_csv(self):
        """
        Load data from CSV file.
        Returns:
            pandas.DataFrame: Data from CSV or empty DataFrame if file doesn't exist.
        """
        lock = FileLock(f"{self.data_file}.lock")
        with lock:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file, parse_dates=['open_time'])
                logger.info(f"Loaded data from {self.data_file}")
                return df
            logger.warning(f"No data file found at {self.data_file}")
            return pd.DataFrame(columns=['open_time', 'open', 'high', 'low', 'close', 'volume'])

    def set_symbol(self, symbol):
        """Update the trading pair symbol and data file path."""
        self.symbol = symbol
        self.data_file = os.path.join(self.data_dir, f"{self.symbol}_{self.interval}.csv")

    def set_interval(self, interval):
        """Update the time interval and data file path."""
        self.interval = interval
        self.data_file = os.path.join(self.data_dir, f"{self.symbol}_{self.interval}.csv")