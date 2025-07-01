import pandas as pd
import numpy as np

class StrategyAgent:
    def __init__(self, df):
        self.df = df.copy()

    def ema_crossover_strategy(self, fast_length=9, slow_length=21):
        """Chiến lược giao cắt EMA."""
        # Tính EMA
        self.df['fast_ema'] = self.df['close'].ewm(span=fast_length, adjust=False).mean()
        self.df['slow_ema'] = self.df['close'].ewm(span=slow_length, adjust=False).mean()

        # Tín hiệu mua/bán
        self.df['signal'] = 0
        self.df['signal'] = np.where(self.df['fast_ema'] > self.df['slow_ema'], 1, -1)

        # Lưu vị trí mua/bán
        self.df['position'] = self.df['signal'].diff()
        return self.df