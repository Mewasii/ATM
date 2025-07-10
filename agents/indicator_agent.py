import pandas as pd
import talib
from filelock import FileLock
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndicatorAgent:
    def __init__(self, data_file):
        """
        Initialize IndicatorAgent with a CSV file path.
        Args:
            data_file: Path to CSV file with price data
        """
        self.data_file = data_file
        self.df = self.load_from_csv()
        self.output_dir = "data/processed"

    def load_from_csv(self):
        """
        Load data from CSV file.
        Returns:
            pandas.DataFrame: Data from CSV
        """
        lock = FileLock(f"{self.data_file}.lock")
        with lock:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file, parse_dates=['open_time'])
                logger.info(f"Loaded data from {self.data_file}")
                return df
            raise ValueError(f"No data file found at {self.data_file}")

    def save_to_csv(self, df, symbol, interval, suffix="indicators"):
        """
        Save DataFrame to CSV with file locking.
        Args:
            df: DataFrame to save
            symbol: Trading pair symbol
            interval: Time interval
            suffix: Suffix for output file name
        """
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, f"{symbol}_{interval}_{suffix}.csv")
        lock = FileLock(f"{output_file}.lock")
        with lock:
            df.to_csv(output_file, index=False)
            logger.info(f"Saved data to {output_file}")

    def calculate_sma(self, length=14, symbol="BTCUSDT", interval="1h"):
        """Calculate Simple Moving Average (SMA) and save to CSV."""
        self.df['sma'] = talib.SMA(self.df['close'], timeperiod=length)
        self.save_to_csv(self.df, symbol, interval, suffix="indicators")
        return self.df

    def calculate_ema(self, length=9, symbol="BTCUSDT", interval="1h"):
        """Calculate Exponential Moving Average (EMA) and save to CSV."""
        self.df['ema'] = talib.EMA(self.df['close'], timeperiod=length)
        self.save_to_csv(self.df, symbol, interval, suffix="indicators")
        return self.df

    def calculate_rsi(self, length=14, symbol="BTCUSDT", interval="1h"):
        """Calculate Relative Strength Index (RSI) and save to CSV."""
        self.df['rsi'] = talib.RSI(self.df['close'], timeperiod=length)
        self.save_to_csv(self.df, symbol, interval, suffix="indicators")
        return self.df

    def calculate_macd(self, fast=12, slow=26, signal=9, symbol="BTCUSDT", interval="1h"):
        """Calculate MACD and save to CSV."""
        self.df['macd'], self.df['macd_signal'], self.df['macd_hist'] = talib.MACD(
            self.df['close'], fastperiod=fast, slowperiod=slow, signalperiod=signal
        )
        self.save_to_csv(self.df, symbol, interval, suffix="indicators")
        return self.df