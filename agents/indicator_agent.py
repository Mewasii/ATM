import pandas as pd
import talib

class IndicatorAgent:
    def __init__(self, df):
        self.df = df.copy()

    def calculate_sma(self, length=14):
        """Tính Simple Moving Average (SMA)."""
        self.df['sma'] = talib.SMA(self.df['close'], timeperiod=length)
        return self.df

    def calculate_ema(self, length=9):
        """Tính Exponential Moving Average (EMA)."""
        self.df['ema'] = talib.EMA(self.df['close'], timeperiod=length)
        return self.df

    def calculate_rsi(self, length=14):
        """Tính Relative Strength Index (RSI)."""
        self.df['rsi'] = talib.RSI(self.df['close'], timeperiod=length)
        return self.df

    def calculate_macd(self, fast=12, slow=26, signal=9):
        """Tính MACD."""
        self.df['macd'], self.df['macd_signal'], self.df['macd_hist'] = talib.MACD(
            self.df['close'], fastperiod=fast, slowperiod=slow, signalperiod=signal
        )
        return self.df