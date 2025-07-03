import pandas as pd
import numpy as np
from strategies.strategy_registry import StrategyRegistry

class StrategyAgent:
    def __init__(self, df):
        self.df = df.copy()

    def apply_strategy(self, strategy_name, **kwargs):
        """Áp dụng chiến lược được chỉ định."""
        if strategy_name.lower() == "ema_crossover":
            return self.ema_crossover_strategy(**kwargs)
        # Thêm các chiến lược khác ở đây, ví dụ:
        # elif strategy_name.lower() == "other_strategy":
        #     return self.other_strategy(**kwargs)
        else:
            raise ValueError(f"Chiến lược '{strategy_name}' không được hỗ trợ.")

    def ema_crossover_strategy(self, fast_length=9, slow_length=21):
        """Chiến lược giao cắt EMA."""
        self.df['fast_ema'] = self.df['close'].ewm(span=fast_length, adjust=False).mean()
        self.df['slow_ema'] = self.df['close'].ewm(span=slow_length, adjust=False).mean()

        self.df['signal'] = 0
        self.df['signal'] = np.where(self.df['fast_ema'] > self.df['slow_ema'], 1, -1)
        self.df['position'] = self.df['signal'].diff()
        return self.df
