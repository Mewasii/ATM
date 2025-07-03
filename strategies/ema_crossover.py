from strategies.base_strategy import BaseStrategy
import backtrader as bt
import pandas as pd
import numpy as np

class EMACrossoverStrategy(BaseStrategy):
    params = (
        ('fast_length', 9),
        ('slow_length', 21),
    )

    def __init__(self):
        self.fast_ema = bt.indicators.EMA(self.data.close, period=self.params.fast_length)
        self.slow_ema = bt.indicators.EMA(self.data.close, period=self.params.slow_length)
        self.equity = []

    def next(self):
        self.equity.append(self.broker.getvalue())
        if self.fast_ema[0] > self.slow_ema[0] and self.fast_ema[-1] <= self.slow_ema[-1]:
            self.buy()
        elif self.fast_ema[0] < self.slow_ema[0] and self.fast_ema[-1] >= self.slow_ema[-1]:
            self.sell()

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['fast_ema'] = df['close'].ewm(span=self.params.fast_length, adjust=False).mean()
        df['slow_ema'] = df['close'].ewm(span=self.params.slow_length, adjust=False).mean()
        df['signal'] = np.where(df['fast_ema'] > df['slow_ema'], 1, -1)
        df['position'] = df['signal'].diff()
        return df