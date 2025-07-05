import pandas as pd
import numpy as np
from strategies.strategy_registry import StrategyRegistry

class StrategyAgent:
    def __init__(self, df):
        self.df = df.copy()
        self.positions = {}  # Store open positions: {entry_id: (quantity, entry_price)}
        self.completed_positions = []  # Store completed positions: [(entry_id, quantity, entry_price, exit_price, profit_loss)]

    def apply_strategy(self, strategy_name, **kwargs):
        """Apply the specified strategy."""
        if strategy_name.lower() == "ema_crossover":
            return self.ema_crossover_strategy(**kwargs)
        else:
            raise ValueError(f"Strategy '{strategy_name}' not supported.")

    def ema_crossover_strategy(self, fast_length=9, slow_length=21, use_ha_df=False, ha_df=None):
        """
        EMA crossover strategy with FIFO and profit/loss tracking.
        Args:
            fast_length: Period for fast EMA
            slow_length: Period for slow EMA
            use_ha_df: If True, use ha_df for calculations
            ha_df: Heikin Ashi DataFrame (optional)
        Returns:
            DataFrame with strategy signals and position details
        """
        calc_df = ha_df.copy() if use_ha_df and ha_df is not None else self.df.copy()
        calc_df['fast_ema'] = calc_df['close' if not use_ha_df else 'ha_close'].ewm(span=fast_length, adjust=False).mean()
        calc_df['slow_ema'] = calc_df['close' if not use_ha_df else 'ha_close'].ewm(span=slow_length, adjust=False).mean()
        calc_df['signal'] = 0
        calc_df['signal'] = np.where(calc_df['fast_ema'] > calc_df['slow_ema'], 1, np.where(calc_df['fast_ema'] < calc_df['slow_ema'], -1, 0))
        calc_df['position_change'] = calc_df['signal'].diff().fillna(0)
        calc_df['position'] = 0  # Initialize position column
        calc_df['entry_id'] = None  # New column to store entry IDs

        entry_id_counter = 1
        for index, row in calc_df.iterrows():
            if row['position_change'] == 2:  # Buy signal
                entry_id = f"#{entry_id_counter:06d}"
                entry_price = row['close' if not use_ha_df else 'ha_close']
                self.positions[entry_id] = (100, entry_price)  # Default quantity of 100
                calc_df.loc[index, 'position'] = 1  # Mark as open long position
                calc_df.loc[index, 'entry_id'] = entry_id  # Store entry ID
                entry_id_counter += 1
            elif row['position_change'] == -2:  # Sell signal
                if self.positions:
                    total_exit_quantity = 100  # Default exit quantity
                    remaining_exit = total_exit_quantity
                    while remaining_exit > 0 and self.positions:
                        earliest_entry_id = min(self.positions.keys())
                        quantity, entry_price = self.positions[earliest_entry_id]
                        exit_quantity = min(remaining_exit, quantity)
                        exit_price = row['close' if not use_ha_df else 'ha_close']
                        profit_loss = exit_quantity * (exit_price - entry_price)
                        self.completed_positions.append((earliest_entry_id, exit_quantity, entry_price, exit_price, profit_loss))
                        calc_df.loc[index, 'position'] = -1  # Mark as exit
                        calc_df.loc[index, 'entry_id'] = earliest_entry_id  # Use exiting entry ID
                        if quantity == exit_quantity:
                            del self.positions[earliest_entry_id]
                        else:
                            self.positions[earliest_entry_id] = (quantity - exit_quantity, entry_price)
                            new_id = f"{earliest_entry_id}a"
                            self.positions[new_id] = (quantity - exit_quantity, entry_price)
                        remaining_exit -= exit_quantity

        calc_df['open_positions'] = [list(self.positions.keys()) if self.positions else [] for _ in range(len(calc_df))]
        calc_df['completed_positions'] = [self.completed_positions.copy() for _ in range(len(calc_df))]
        return calc_df