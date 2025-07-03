import pandas as pd
import numpy as np

class StrategyAgent:
    def __init__(self, df):
        self.df = df.copy()

    def ema_crossover_strategy(self, fast_length=9, slow_length=21, use_ha_df=False, ha_df=None):
        """
        EMA crossover strategy, using either df or ha_df.
        Args:
            fast_length: Period for fast EMA
            slow_length: Period for slow EMA
            use_ha_df: If True, use ha_df for calculations
            ha_df: Heikin Ashi DataFrame
        Returns:
            DataFrame with strategy signals
        """
        calc_df = ha_df.copy() if use_ha_df and ha_df is not None else self.df.copy()
        calc_df['fast_ema'] = calc_df['close' if not use_ha_df else 'ha_close'].ewm(span=fast_length, adjust=False).mean()
        calc_df['slow_ema'] = calc_df['close' if not use_ha_df else 'ha_close'].ewm(span=slow_length, adjust=False).mean()
        calc_df['signal'] = 0
        calc_df['signal'] = np.where(calc_df['fast_ema'] > calc_df['slow_ema'], 1, -1)
        calc_df['position'] = calc_df['signal'].diff()
        return calc_df