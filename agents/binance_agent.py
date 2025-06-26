import pandas as pd
from binance.client import Client
from utils.config import Config

class BinanceAgent:
    def __init__(self):
        self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)
        self.symbol = Config.DEFAULT_SYMBOL
        self.interval = Config.DEFAULT_INTERVAL

    def fetch_klines(self, limit=100):
        """
        Fetch historical kline data for the specified symbol and interval.
        Args:
            limit (int): Number of data points to fetch.
        Returns:
            pandas.DataFrame: Kline data with columns [open_time, open, high, low, close, volume].
        """
        klines = self.client.get_klines(symbol=self.symbol, interval=self.interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        # Convert only numeric columns to float
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].astype(float)
        return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]

    def set_symbol(self, symbol):
        """Update the trading pair symbol."""
        self.symbol = symbol

    def set_interval(self, interval):
        """Update the time interval (e.g., '1m', '1h', '1d')."""
        self.interval = interval